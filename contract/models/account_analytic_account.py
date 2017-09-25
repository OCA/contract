# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account',
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
    date_start = fields.Date(default=fields.Date.context_today)
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

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `recurring_invoice_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """

        contract = self.contract_template_id

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

    @api.onchange('recurring_invoices')
    def _onchange_recurring_invoices(self):
        if self.date_start and self.recurring_invoices:
            self.recurring_next_date = self.date_start

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id

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
    def _insert_markers(self, line, date_start, next_date, date_format):
        contract = line.analytic_account_id
        if contract.recurring_invoicing_type == 'pre-paid':
            date_from = date_start
            date_to = next_date - relativedelta(days=1)
        else:
            date_from = (date_start -
                         self.get_relative_delta(contract.recurring_rule_type,
                                                 contract.recurring_interval) +
                         relativedelta(days=1))
            date_to = date_start
        name = line.name
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
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        # Insert markers
        name = line.name
        contract = line.analytic_account_id
        if 'old_date' in self.env.context and 'next_date' in self.env.context:
            lang_obj = self.env['res.lang']
            lang = lang_obj.search(
                [('code', '=', contract.partner_id.lang)])
            date_format = lang.date_format or '%m/%d/%Y'
            name = self._insert_markers(
                line, self.env.context['old_date'],
                self.env.context['next_date'], date_format)
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
        invoice_vals = self._prepare_invoice()
        invoice = self.env['account.invoice'].create(invoice_vals)
        for line in self.recurring_invoice_line_ids:
            invoice_line_vals = self._prepare_invoice_line(line, invoice.id)
            self.env['account.invoice.line'].create(invoice_line_vals)
        invoice.compute_taxes()
        return invoice

    @api.multi
    def recurring_create_invoice(self):
        for contract in self:
            old_date = fields.Date.from_string(
                contract.recurring_next_date or fields.Date.today())
            new_date = old_date + self.get_relative_delta(
                contract.recurring_rule_type, contract.recurring_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                # Force company for correct evaluate domain access rules
                'force_company': contract.company_id.id,
            })
            # Re-read contract with correct company
            contract.with_context(ctx)._create_invoice()
            contract.write({
                'recurring_next_date': new_date.strftime('%Y-%m-%d')
            })
        return True

    @api.model
    def cron_recurring_create_invoice(self):
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('recurring_invoices', '=', True)])
        return contracts.recurring_create_invoice()

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
