# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


class ContractContract(models.Model):
    _name = 'contract.contract'
    _description = "Contract"
    _order = 'code, name asc'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'contract.abstract.contract',
        'portal.mixin'
    ]

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char(
        string="Reference",
    )
    group_id = fields.Many2one(
        string="Group",
        comodel_name='account.analytic.account',
        ondelete='restrict',
    )
    currency_id = fields.Many2one(
        compute="_compute_currency_id",
        inverse="_inverse_currency_id",
        comodel_name="res.currency",
        string="Currency",
    )
    manual_currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
    )
    contract_template_id = fields.Many2one(
        string='Contract Template', comodel_name='contract.template'
    )
    contract_line_ids = fields.One2many(
        string='Contract lines',
        comodel_name='contract.line',
        inverse_name='contract_id',
        copy=True,
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
    date_start = fields.Date(
        compute='_compute_date_end', string='Date Start', store=True
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', string='Payment Terms', index=True
    )
    invoice_count = fields.Integer(compute="_compute_invoice_count")
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position',
        ondelete='restrict',
    )
    invoice_partner_id = fields.Many2one(
        string="Invoicing contact",
        comodel_name='res.partner',
        ondelete='restrict',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        inverse='_inverse_partner_id',
        required=True
    )

    commercial_partner_id = fields.Many2one(
        'res.partner',
        compute_sudo=True,
        related='partner_id.commercial_partner_id',
        store=True,
        string='Commercial Entity',
        index=True
    )
    tag_ids = fields.Many2many(comodel_name="contract.tag", string="Tags")
    note = fields.Text(string="Notes")
    is_terminated = fields.Boolean(
        string="Terminated", readonly=True, copy=False
    )
    terminate_reason_id = fields.Many2one(
        comodel_name="contract.terminate.reason",
        string="Termination Reason",
        ondelete="restrict",
        readonly=True,
        copy=False,
        track_visibility="onchange",
    )
    terminate_comment = fields.Text(
        string="Termination Comment",
        readonly=True,
        copy=False,
        track_visibility="onchange",
    )
    terminate_date = fields.Date(
        string="Termination Date",
        readonly=True,
        copy=False,
        track_visibility="onchange",
    )
    modification_ids = fields.One2many(
        comodel_name='contract.modification',
        inverse_name='contract_id',
        string='Modifications',
    )

    def get_formview_id(self, access_uid=None):
        if self.contract_type == "sale":
            return self.env.ref("contract.contract_contract_customer_form_view").id
        else:
            return self.env.ref("contract.contract_contract_supplier_form_view").id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._set_start_contract_modification()
        return records

    def write(self, vals):
        if 'modification_ids' in vals:
            res = super(ContractContract, self.with_context(
                bypass_modification_send=True
            )).write(vals)
            self._modification_mail_send()
        else:
            res = super(ContractContract, self).write(vals)
        return res

    @api.model
    def _set_start_contract_modification(self):
        subtype_id = self.env.ref('contract.mail_message_subtype_contract_modification')
        for record in self:
            if record.contract_line_ids:
                date_start = min(record.contract_line_ids.mapped('date_start'))
            else:
                date_start = record.create_date
            record.message_subscribe(
                partner_ids=[record.partner_id.id],
                subtype_ids=[subtype_id.id]
            )
            record.with_context(skip_modification_mail=True).write({
                'modification_ids': [
                    (0, 0, {'date': date_start, 'description': _('Contract start')})
                ]
            })

    @api.model
    def _modification_mail_send(self):
        for record in self:
            modification_ids_not_sent = record.modification_ids.filtered(
                lambda x: not x.sent
            )
            if modification_ids_not_sent:
                if not self.env.context.get('skip_modification_mail'):
                    record.with_context(
                        default_subtype_id=self.env.ref(
                            'contract.mail_message_subtype_contract_modification'
                        ).id,
                    ).message_post_with_template(
                        self.env.ref(
                            "contract.mail_template_contract_modification"
                        ).id,
                        notif_layout="contract.template_contract_modification",
                    )
                modification_ids_not_sent.write({'sent': True})

    @api.multi
    def _inverse_partner_id(self):
        for rec in self:
            if not rec.invoice_partner_id:
                rec.invoice_partner_id = rec.partner_id.address_get(
                    ['invoice']
                )['invoice']

    @api.multi
    def _get_related_invoices(self):
        self.ensure_one()

        invoices = (
            self.env['account.invoice.line']
            .search(
                [
                    (
                        'contract_line_id',
                        'in',
                        self.contract_line_ids.ids,
                    )
                ]
            )
            .mapped('invoice_id')
        )
        invoices |= self.env['account.invoice'].search(
            [('old_contract_id', '=', self.id)]
        )
        return invoices

    def _get_computed_currency(self):
        """Helper method for returning the theoretical computed currency."""
        self.ensure_one()
        currency = self.env['res.currency']
        if any(self.contract_line_ids.mapped('automatic_price')):
            # Use pricelist currency
            currency = (
                self.pricelist_id.currency_id or
                self.partner_id.with_context(
                    force_company=self.company_id.id,
                ).property_product_pricelist.currency_id
            )
        return (
            currency or self.journal_id.currency_id or
            self.company_id.currency_id
        )

    @api.depends(
        "manual_currency_id",
        "pricelist_id",
        "partner_id",
        "journal_id",
        "company_id",
    )
    def _compute_currency_id(self):
        for rec in self:
            if rec.manual_currency_id:
                rec.currency_id = rec.manual_currency_id
            else:
                rec.currency_id = rec._get_computed_currency()

    def _inverse_currency_id(self):
        """If the currency is different from the computed one, then save it
        in the manual field.
        """
        for rec in self:
            if rec._get_computed_currency() != rec.currency_id:
                rec.manual_currency_id = rec.currency_id
            else:
                rec.manual_currency_id = False

    @api.multi
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec._get_related_invoices())

    @api.multi
    def action_show_invoices(self):
        self.ensure_one()
        tree_view_ref = (
            'account.invoice_supplier_tree'
            if self.contract_type == 'purchase'
            else 'account.invoice_tree_with_onboarding'
        )
        form_view_ref = (
            'account.invoice_supplier_form'
            if self.contract_type == 'purchase'
            else 'account.invoice_form'
        )
        tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        form_view = self.env.ref(form_view_ref, raise_if_not_found=False)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'domain': [('id', 'in', self._get_related_invoices().ids)],
        }
        if tree_view and form_view:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action

    @api.depends('contract_line_ids.date_end')
    def _compute_date_end(self):
        for contract in self:
            contract.date_end = False
            date_end = contract.contract_line_ids.mapped('date_end')
            if date_end and all(date_end):
                contract.date_end = max(date_end)
            date_start = False
            if contract.contract_line_ids:
                date_start = min(contract.contract_line_ids.mapped('date_start'))
            contract.date_start = date_start

    @api.depends(
        'contract_line_ids.recurring_next_date',
        'contract_line_ids.is_canceled',
    )
    def _compute_recurring_next_date(self):
        for contract in self:
            recurring_next_date = contract.contract_line_ids.filtered(
                lambda l: (l.recurring_next_date and not l.is_canceled
                           and (not l.display_type or l.is_recurring_note))
            ).mapped('recurring_next_date')
            if recurring_next_date:
                contract.recurring_next_date = min(recurring_next_date)

    @api.depends('contract_line_ids.create_invoice_visibility')
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = any(
                contract.contract_line_ids.mapped(
                    'create_invoice_visibility'
                )
            )

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `contract_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """
        contract_template_id = self.contract_template_id
        if not contract_template_id:
            return
        for field_name, field in contract_template_id._fields.items():
            if field.name == 'contract_line_ids':
                lines = self._convert_contract_lines(contract_template_id)
                self.contract_line_ids += lines
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
                if self.contract_template_id[field_name]:
                    self[field_name] = self.contract_template_id[field_name]

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        partner = (
            self.partner_id
            if not self.company_id
            else self.partner_id.with_context(force_company=self.company_id.id)
        )
        self.pricelist_id = partner.property_product_pricelist.id
        self.fiscal_position_id = partner.env[
            'account.fiscal.position'
        ].get_fiscal_position(partner.id)
        if self.contract_type == 'purchase':
            self.payment_term_id = partner.property_supplier_payment_term_id
        else:
            self.payment_term_id = partner.property_payment_term_id
        self.invoice_partner_id = self.partner_id.address_get(['invoice'])[
            'invoice'
        ]
        return {
            'domain': {
                'invoice_partner_id': [
                    '|',
                    ('id', 'parent_of', self.partner_id.id),
                    ('id', 'child_of', self.partner_id.id),
                ]
            }
        }

    @api.multi
    def _convert_contract_lines(self, contract):
        self.ensure_one()
        new_lines = self.env['contract.line']
        contract_line_model = self.env['contract.line']
        for contract_line in contract.contract_line_ids:
            vals = contract_line._convert_to_write(contract_line.read()[0])
            # Remove template link field
            vals.pop('contract_template_id', False)
            vals['date_start'] = fields.Date.context_today(contract_line)
            vals['recurring_next_date'] = fields.Date.context_today(
                contract_line
            )
            new_lines += contract_line_model.new(vals)
        new_lines._onchange_date_start()
        new_lines._onchange_is_auto_renew()
        return new_lines

    @api.multi
    def _prepare_invoice(self, date_invoice, journal=None):
        self.ensure_one()
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
        invoice_type = 'out_invoice'
        if self.contract_type == 'purchase':
            invoice_type = 'in_invoice'
        vinvoice = self.env['account.invoice'].with_context(
            force_company=self.company_id.id,
        ).new({
            'company_id': self.company_id.id,
            'partner_id': self.invoice_partner_id.id,
            'type': invoice_type,
        })
        vinvoice._onchange_partner_id()
        invoice_vals = vinvoice._convert_to_write(vinvoice._cache)
        invoice_vals.update({
            'name': self.code,
            'currency_id': self.currency_id.id,
            'date_invoice': date_invoice,
            'journal_id': journal.id,
            'origin': self.name,
            'user_id': self.user_id.id,
        })
        if self.payment_term_id:
            invoice_vals['payment_term_id'] = self.payment_term_id.id
        if self.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id
        return invoice_vals

    @api.multi
    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref('contract.email_contract_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='contract.contract',
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
        """Provided for keeping compatibility in this version."""
        # TODO: Must be removed in >=13.0
        return invoice_values

    @api.model
    def _finalize_invoice_creation(self, invoices):
        """This method is called right after the creation of the invoices.

        Override it when you need to do something after the records are created
        in the DB. If you need to modify any value, better to do it on the
        _prepare_* methods on contract or contract line.
        """
        invoices.compute_taxes()

    @api.model
    def _invoice_followers(self, invoices):
        invoice_create_subtype = self.sudo().env.ref(
            'contract.mail_message_subtype_invoice_created'
        )
        for item in self:
            partner_ids = item.message_follower_ids.filtered(
                lambda x: invoice_create_subtype in x.subtype_ids
            ).mapped('partner_id')
            if partner_ids:
                (
                    invoices & item._get_related_invoices()
                ).message_subscribe(partner_ids=partner_ids.ids)

    @api.model
    def _finalize_and_create_invoices(self, invoices_values):
        """This method:

         - creates the invoices
         - finalizes the created invoices (tax computation...)

        :param invoices_values: list of dictionaries (invoices values)
        :return: created invoices (account.invoice)
        """
        final_invoices_values = []
        # TODO: This call must be removed in >=13.0
        for invoice_values in invoices_values:
            final_invoices_values.append(
                self._finalize_invoice_values(invoice_values)
            )
        invoices = self.env['account.invoice'].create(final_invoices_values)
        self._finalize_invoice_creation(invoices)
        self._invoice_followers(invoices)
        return invoices

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        """
        This method builds the domain to use to find all
        contracts (contract.contract) to invoice.
        :param date_ref: optional reference date to use instead of today
        :return: list (domain) usable on contract.contract
        """
        domain = []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain.extend([('recurring_next_date', '<=', date_ref)])
        return domain

    @api.multi
    def _get_lines_to_invoice(self, date_ref):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (contract.line recordset)
        """
        self.ensure_one()

        def can_be_invoiced(l):
            return (not l.is_canceled and l.recurring_next_date
                    and l.recurring_next_date <= date_ref)

        lines2invoice = previous = self.env['contract.line']
        current_section = current_note = False
        for line in self.contract_line_ids:
            if line.display_type == 'line_section':
                current_section = line
            elif (line.display_type == 'line_note' and
                    not line.is_recurring_note):
                if line.note_invoicing_mode == "with_previous_line":
                    if previous in lines2invoice:
                        lines2invoice |= line
                    current_note = False
                elif line.note_invoicing_mode == "with_next_line":
                    current_note = line
            elif line.is_recurring_note or not line.display_type:
                if can_be_invoiced(line):
                    if current_section:
                        lines2invoice |= current_section
                        current_section = False
                    if current_note:
                        lines2invoice |= current_note
                    lines2invoice |= line
                    current_note = False
            previous = line
        return lines2invoice.sorted()

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
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            invoice_values = contract._prepare_invoice(date_ref)
            for line in contract_lines:
                invoice_values.setdefault('invoice_line_ids', [])
                invoice_line_values = line._prepare_invoice_line(
                    invoice_values=invoice_values,
                )
                if invoice_line_values:
                    invoice_values['invoice_line_ids'].append(
                        (0, 0, invoice_line_values)
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
        invoices = self._recurring_create_invoice()
        if invoices:
            for invoice in invoices:
                self.message_post(
                    body=_(
                        'Contract manually invoiced: '
                        '<a href="#" data-oe-model="%s" data-oe-id="%s">Invoice'
                        '</a>'
                    )
                    % (invoice._name, invoice.id)
                )
        return invoices

    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        return self._finalize_and_create_invoices(invoices_values)

    @api.model
    def cron_recurring_create_invoice(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = self._get_contracts_to_invoice_domain(date_ref)
        invoices = self.env["account.invoice"]
        # Invoice by companies, so assignation emails get correct context
        companies_to_invoice = self.read_group(domain, ["company_id"], ["company_id"])
        for row in companies_to_invoice:
            contracts_to_invoice = self.search(row["__domain"]).with_context(
                allowed_company_ids=[row["company_id"][0]]
            ).filtered(
                lambda a: not a.date_end or a.recurring_next_date <= a.date_end
            )
            invoices |= contracts_to_invoice._recurring_create_invoice(date_ref)
        return invoices

    @api.multi
    def action_terminate_contract(self):
        self.ensure_one()
        context = {"default_contract_id": self.id}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Terminate Contract'),
            'res_model': 'contract.contract.terminate',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    @api.multi
    def _terminate_contract(
        self, terminate_reason_id, terminate_comment, terminate_date
    ):
        self.ensure_one()
        if not self.env.user.has_group("contract.can_terminate_contract"):
            raise UserError(_('You are not allowed to terminate contracts.'))
        self.contract_line_ids.filtered('is_stop_allowed').stop(terminate_date)
        self.write({
            'is_terminated': True,
            'terminate_reason_id': terminate_reason_id.id,
            'terminate_comment': terminate_comment,
            'terminate_date': terminate_date,
        })
        return True

    @api.multi
    def action_cancel_contract_termination(self):
        self.ensure_one()
        self.write({
            'is_terminated': False,
            'terminate_reason_id': False,
            'terminate_comment': False,
            'terminate_date': False,
        })

    def _compute_access_url(self):
        for record in self:
            record.access_url = '/my/contracts/{}'.format(record.id)

    def action_preview(self):
        """Invoked when 'Preview' button in contract form view is clicked."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
