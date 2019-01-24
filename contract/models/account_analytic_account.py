# -*- coding: utf-8 -*-
# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=no-member

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = [
        'account.analytic.account',
        'account.analytic.contract',
    ]

    contract_template_id = fields.Many2one(
        string='Contract Template',
        comodel_name='account.analytic.contract',
    )
    recurring_invoice_line_ids = fields.One2many(
        string='Invoice Lines',
        comodel_name='account.analytic.invoice.line',
        inverse_name='analytic_account_id',
        copy=True,
    )
    date_start = fields.Date(
        string='Date Start',
        default=fields.Date.context_today,
    )
    date_end = fields.Date(
        string='Date End',
        index=True,
    )
    recurring_invoices = fields.Boolean(
        string='Generate recurring invoices automatically',
    )
    recurring_next_date = fields.Date(
        default=fields.Date.context_today,
        copy=False,
        string='Date of Next Invoice',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    create_invoice_visibility = fields.Boolean(
        compute='_compute_create_invoice_visibility',
    )

    @api.depends('recurring_next_date', 'date_end')
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = (
                not contract.date_end or
                contract.recurring_next_date <= contract.date_end
            )

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `recurring_invoice_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """
        contract = self.contract_template_id
        if not contract:
            return
        for field_name, field in contract._fields.iteritems():
            if field.name == 'recurring_invoice_line_ids':
                lines = self._convert_contract_lines(contract)
                self.recurring_invoice_line_ids = lines
            elif not any((
                field.compute, field.related, field.automatic,
                field.readonly, field.company_dependent,
                field.name in self.NO_SYNC,
            )):
                self[field_name] = self.contract_template_id[field_name]

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.recurring_next_date = self.date_start

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.constrains('partner_id', 'recurring_invoices')
    def _check_partner_id_recurring_invoices(self):
        for contract in self.filtered('recurring_invoices'):
            if not contract.partner_id:
                raise ValidationError(
                    _("You must supply a customer for the contract '%s'") %
                    contract.name
                )

    @api.constrains('recurring_next_date', 'date_start')
    def _check_recurring_next_date_start_date(self):
        for contract in self.filtered('recurring_next_date'):
            if contract.date_start > contract.recurring_next_date:
                raise ValidationError(
                    _("You can't have a next invoicing date before the start "
                      "of the contract '%s'") % contract.name
                )

    @api.constrains('recurring_next_date', 'recurring_invoices')
    def _check_recurring_next_date_recurring_invoices(self):
        for contract in self.filtered('recurring_invoices'):
            if not contract.recurring_next_date:
                raise ValidationError(
                    _("You must supply a next invoicing date for contract "
                      "'%s'") % contract.name
                )

    @api.constrains('date_start', 'recurring_invoices')
    def _check_date_start_recurring_invoices(self):
        for contract in self.filtered('recurring_invoices'):
            if not contract.date_start:
                raise ValidationError(
                    _("You must supply a start date for contract '%s'") %
                    contract.name
                )

    @api.constrains('date_start', 'date_end')
    def _check_start_end_dates(self):
        for contract in self.filtered('date_end'):
            if contract.date_start > contract.date_end:
                raise ValidationError(
                    _("Contract '%s' start date can't be later than end date")
                    % contract.name
                )

    @api.multi
    def _convert_contract_lines(self, contract):
        self.ensure_one()
        new_lines = []
        for contract_line in contract.recurring_invoice_line_ids:
            vals = contract_line._convert_to_write(contract_line.read()[0])
            new_lines.append((0, 0, vals))
        return new_lines

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        if recurring_rule_type == 'daily':
            return relativedelta(days=interval)
        elif recurring_rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif recurring_rule_type == 'monthly':
            return relativedelta(months=interval)
        elif recurring_rule_type == 'monthlylastday':
            return relativedelta(months=interval, day=31)
        else:
            return relativedelta(years=interval)

    @api.model
    def _insert_markers(self, name):
        """Replace markers in contract or line with dates from context.

        This can be used either for the generation of invoice values
        or for invoice line values.
        """
        self.ensure_one()
        context = self.env.context if 'date_format' in self.env.context \
            else self.get_invoice_context()
        date_format = context.get('date_format', '%m/%d/%Y')
        date_from = context['date_from']
        date_to = context['date_to']
        name = name.replace('#START#', date_from.strftime(date_format))
        name = name.replace('#END#', date_to.strftime(date_format))
        return name

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id,
            'discount': line.discount,
        })
        # Add analytic tags to invoice line
        invoice_line.analytic_tag_ids |= line.analytic_tag_ids
        # Get some invoice line values from relevant parts of
        # onchange_product_id (for performance reasons inlined here).
        invoice = invoice_line.invoice_id
        account = invoice_line.get_invoice_line_account(
            invoice.type,
            invoice_line.product_id,
            invoice.fiscal_position_id,
            invoice.company_id)
        if account:
            invoice_line.account_id = account.id
        invoice_line._set_taxes()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        # Insert markers
        contract = line.analytic_account_id
        name = self._insert_markers(line.name)
        invoice_line_vals.update({
            'name': name,
            'account_analytic_id': contract.id,
            'price_unit': line.price_unit,
        })
        return invoice_line_vals

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(
                _("You must first select a Customer for Contract %s!") %
                self.name)
        journal = self.journal_id or self.env['account.journal'].search(
            [('type', '=', 'sale'),
             ('company_id', '=', self.company_id.id)],
            limit=1)
        if not journal:
            raise ValidationError(
                _("Please define a sale journal for the company '%s'.") %
                (self.company_id.name or '',))
        currency = (
            self.pricelist_id.currency_id or
            self.partner_id.property_product_pricelist.currency_id or
            self.company_id.currency_id
        )
        invoice = self.env['account.invoice'].new({
            'reference': self.code,
            'type': 'out_invoice',
            'partner_id': self.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': self.recurring_next_date,
            'origin': self.name,
            'company_id': self.company_id.id,
            'contract_id': self.id,
            'user_id': self.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        # Re-read contract with correct company
        _self = self.with_context(self.get_invoice_context())
        invoice_vals = _self._prepare_invoice()
        invoice = _self.env['account.invoice'].create(invoice_vals)
        # Lines are read from an env where expensive values are precomputed
        for line in self.recurring_invoice_line_ids:
            invoice_line_vals = _self._prepare_invoice_line(line, invoice.id)
            _self.env['account.invoice.line'].create(invoice_line_vals)
        # Update next invoice date for current contract
        _self.recurring_next_date = _self.env.context['next_date']
        return invoice

    @api.multi
    def get_invoice_context(self):
        """Compute context for invoice creation."""
        self.ensure_one()
        ctx = self.env.context.copy()
        ref_date = self.recurring_next_date or fields.Date.today()
        date_start = fields.Date.from_string(ref_date)
        next_date = date_start + self.get_relative_delta(
            self.recurring_rule_type, self.recurring_interval)
        lang_obj = self.env['res.lang']
        code = self.partner_id.lang or self.company_id.partner_id.lang
        lang = lang_obj.search([('code', '=', code)])
        date_format = lang.date_format or '%m/%d/%Y'
        if self.recurring_invoicing_type == 'pre-paid':
            date_from = date_start
            date_to = next_date - relativedelta(days=1)
        else:
            date_from = (
                date_start -
                self.get_relative_delta(
                    self.recurring_rule_type, self.recurring_interval) +
                relativedelta(days=1))
            date_to = date_start
        ctx.update({
            'mail_notrack': True,
            'next_date': next_date,
            'date_format': date_format,
            'date_from': date_from,
            'date_to': date_to,
            # Force company for correct evaluation of domain access rules
            'force_company': self.company_id.id})
        return ctx

    @api.multi
    def check_dates_valid(self):
        """Check start and end dates."""
        self.ensure_one()
        ref_date = self.recurring_next_date or fields.Date.today()
        if (self.date_start > ref_date or
                self.date_end and self.date_end < ref_date):
            if self.env.context.get('cron'):
                return False  # Don't fail on cron jobs
            raise ValidationError(
                _("You must review start and end dates!\n%s") % self.name)
        return True

    @api.multi
    def recurring_create_invoice(self, limit=None):
        """Create invoices from contracts

        :param int limit:
            Max of invoices to create.

        :return: invoices created
        """
        _self = self.with_context(prefetch_fields=False)
        invoices = _self.env['account.invoice']
        # Precompute expensive computed fields in batch
        recurring_lines = _self.mapped("recurring_invoice_line_ids")
        recurring_lines._fields["price_unit"].determine_value(recurring_lines)
        # Create invoices
        with _self.env.norecompute():
            for contract in _self:
                if limit and len(invoices) >= limit:
                    break
                if not contract.check_dates_valid():
                    continue
                invoices |= contract._create_invoice()
            invoices.compute_taxes()
        _self.recompute()
        return invoices

    @api.model
    def cron_recurring_create_invoice(self, limit=None):
        today = fields.Date.today()
        contracts = self.with_context(cron=True).search([
            ('recurring_invoices', '=', True),
            ('recurring_next_date', '<=', today),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', today),
        ])
        return contracts.recurring_create_invoice(limit)

    @api.multi
    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref(
            'contract.email_contract_template',
            False,
        )
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
