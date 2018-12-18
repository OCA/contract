# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = [
        'account.analytic.account',
        'account.abstract.analytic.contract',
    ]

    contract_template_id = fields.Many2one(
        string='Contract Template', comodel_name='account.analytic.contract'
    )
    recurring_invoice_line_ids = fields.One2many(
        string='Invoice Lines',
        comodel_name='account.analytic.invoice.line',
        inverse_name='contract_id',
        copy=True,
    )
    recurring_invoices = fields.Boolean(
        string='Generate recurring invoices automatically'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    create_invoice_visibility = fields.Boolean(
        compute='_compute_create_invoice_visibility'
    )
    recurring_next_date = fields.Date(
        compute='_compute_recurring_next_date',
        string='Date of Next Invoice',
        store=True,
    )
    date_end = fields.Date(
        compute='_compute_date_end', string='Date End', store=True
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Terms',
    )

    @api.depends('recurring_invoice_line_ids.date_end')
    def _compute_date_end(self):
        for contract in self:
            contract.date_end = False
            date_end = contract.recurring_invoice_line_ids.mapped('date_end')
            if date_end and all(date_end):
                contract.date_end = max(date_end)

    @api.depends(
        'recurring_invoice_line_ids.recurring_next_date',
        'recurring_invoice_line_ids.is_canceled',
    )
    def _compute_recurring_next_date(self):
        for contract in self:
            recurring_next_date = contract.recurring_invoice_line_ids.filtered(
                lambda l: l.recurring_next_date and not l.is_canceled
            ).mapped('recurring_next_date')
            if recurring_next_date:
                contract.recurring_next_date = min(recurring_next_date)

    @api.depends('recurring_invoice_line_ids.create_invoice_visibility')
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = any(
                contract.recurring_invoice_line_ids.mapped(
                    'create_invoice_visibility'
                )
            )

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `recurring_invoice_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """
        contract_template_id = self.contract_template_id
        if not contract_template_id:
            return
        for field_name, field in contract_template_id._fields.items():
            if field.name == 'recurring_invoice_line_ids':
                lines = self._convert_contract_lines(contract_template_id)
                self.recurring_invoice_line_ids = lines
            elif not any(
                (
                    field.compute,
                    field.related,
                    field.automatic,
                    field.readonly,
                    field.company_dependent,
                    field.name in self.NO_SYNC,
                )
            ):
                self[field_name] = self.contract_template_id[field_name]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.constrains('partner_id', 'recurring_invoices')
    def _check_partner_id_recurring_invoices(self):
        for contract in self.filtered('recurring_invoices'):
            if not contract.partner_id:
                raise ValidationError(
                    _("You must supply a customer for the contract '%s'")
                    % contract.name
                )

    @api.multi
    def _convert_contract_lines(self, contract):
        self.ensure_one()
        new_lines = []
        for contract_line in contract.recurring_invoice_line_ids:
            vals = contract_line._convert_to_write(contract_line.read()[0])
            # Remove template link field
            vals.pop('contract_template_id', False)
            vals['date_start'] = fields.Date.context_today(contract_line)
            vals['recurring_next_date'] = fields.Date.context_today(
                contract_line
            )
            self.recurring_invoice_line_ids._onchange_date_start()
            new_lines.append((0, 0, vals))
        return new_lines

    @api.multi
    def _prepare_invoice(self, date_invoice, journal=None):
        self.ensure_one()
        if not self.partner_id:
            if self.contract_type == 'purchase':
                raise ValidationError(
                    _("You must first select a Supplier for Contract %s!")
                    % self.name
                )
            else:
                raise ValidationError(
                    _("You must first select a Customer for Contract %s!")
                    % self.name
                )
        if not journal:
            journal = (
                self.journal_id
                if self.journal_id.type == self.contract_type
                else self.env['account.journal'].search(
                    [
                        ('type', '=', self.contract_type),
                        ('company_id', '=', self.company_id.id),
                    ],
                    limit=1,
                )
            )
        if not journal:
            raise ValidationError(
                _("Please define a %s journal for the company '%s'.")
                % (self.contract_type, self.company_id.name or '')
            )
        currency = (
            self.pricelist_id.currency_id
            or self.partner_id.property_product_pricelist.currency_id
            or self.company_id.currency_id
        )
        invoice_type = 'out_invoice'
        if self.contract_type == 'purchase':
            invoice_type = 'in_invoice'
        return {
            'reference': self.code,
            'type': invoice_type,
            'partner_id': self.partner_id.address_get(['invoice'])[
                'invoice'
            ],
            'currency_id': currency.id,
            'date_invoice': date_invoice,
            'journal_id': journal.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'contract_id': self.id,
            'user_id': self.partner_id.user_id.id,
        }

    @api.multi
    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref('contract.email_contract_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='account.analytic.account',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _finalize_invoice_values(self, invoice_values):
        """
        This method adds the missing values in the invoice lines dictionaries.

        If no account on the product, the invoice lines account is
        taken from the invoice's journal in _onchange_product_id
        This code is not in finalize_creation_from_contract because it's
        not possible to create an invoice line with no account

        :param invoice_values: dictionary (invoice values)
        :return: updated dictionary (invoice values)
        """
        # If no account on the product, the invoice lines account is
        # taken from the invoice's journal in _onchange_product_id
        # This code is not in finalize_creation_from_contract because it's
        # not possible to create an invoice line with no account
        new_invoice = self.env['account.invoice'].new(invoice_values)
        for invoice_line in new_invoice.invoice_line_ids:
            name = invoice_line.name
            account_analytic_id = invoice_line.account_analytic_id
            price_unit = invoice_line.price_unit
            invoice_line.invoice_id = new_invoice
            invoice_line._onchange_product_id()
            invoice_line.update({
                'name': name,
                'account_analytic_id': account_analytic_id,
                'price_unit': price_unit,
            })
        return new_invoice._convert_to_write(new_invoice._cache)

    @api.model
    def _finalize_invoice_creation(self, invoices):
        for invoice in invoices:
            invoice._onchange_partner_id()
        invoices.compute_taxes()

    @api.model
    def _finalize_and_create_invoices(self, invoices_values):
        """
        This method:
         - finalizes the invoices values (onchange's...)
         - creates the invoices
         - finalizes the created invoices (onchange's, tax computation...)
        :param invoices_values: list of dictionaries (invoices values)
        :return: created invoices (account.invoice)
        """
        if isinstance(invoices_values, dict):
            invoices_values = [invoices_values]
        final_invoices_values = []
        for invoice_values in invoices_values:
            final_invoices_values.append(
                self._finalize_invoice_values(invoice_values))
        invoices = self.env['account.invoice'].create(final_invoices_values)
        self._finalize_invoice_creation(invoices)
        return invoices

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        """
        This method builds the domain to use to find all
        contracts (account.analytic.account) to invoice.
        :param date_ref: optional reference date to use instead of today
        :return: list (domain) usable on account.analytic.account
        """
        domain = []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain.extend(
            [
                ('recurring_invoices', '=', True),
                ('recurring_next_date', '<=', date_ref),
            ]
        )
        return domain

    @api.multi
    def _get_lines_to_invoice(self, date_ref):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (account.analytic.invoice.line recordset)
        """
        self.ensure_one()
        return self.recurring_invoice_line_ids.filtered(
            lambda l: not l.is_canceled and l.recurring_next_date
            and l.recurring_next_date <= date_ref)

    @api.multi
    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        invoices_values = []
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            invoice_values = contract._prepare_invoice(date_ref)
            for line in contract_lines:
                invoice_values.setdefault('invoice_line_ids', [])
                invoice_values['invoice_line_ids'].append(
                    (0, 0, line._prepare_invoice_line(invoice_id=False))
                )
            invoices_values.append(invoice_values)
            contract_lines._update_recurring_next_date()
        return invoices_values

    @api.multi
    def recurring_create_invoice(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        return self._recurring_create_invoice()

    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        return self._finalize_and_create_invoices(invoices_values)

    @api.model
    def cron_recurring_create_invoice(self):
        domain = self._get_contracts_to_invoice_domain()
        contracts_to_invoice = self.search(domain)
        date_ref = fields.Date.context_today(contracts_to_invoice)
        contracts_to_invoice._recurring_create_invoice(date_ref)
