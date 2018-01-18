# -*- coding: utf-8 -*-
# Copyright 2018 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    auto_cancel_contract = fields.Boolean(
        string='Auto Cancel',
        help='Enabling will cause the contract recurring '
             'invoices option to be disabled (effectively '
             'canceling the contract) when an invoice is '
             'past due.',
    )
    past_due_invoice_ids = fields.One2many(
        string='Past Due Invoices',
        comodel_name='account.invoice',
        compute='_compute_past_due_invoice_ids',
    )

    @api.multi
    def recurring_create_invoice(self):

        contracts = self.filtered(lambda s: s.auto_cancel_contract)

        for contract in contracts:
            if contract.past_due_invoice_ids:
                contract.recurring_invoices = False
                self -= contract

        if self:
            return super(AccountAnalyticAccount, self) \
                .recurring_create_invoice()

    @api.multi
    def _compute_past_due_invoice_ids(self):

        Invoice = self.env['account.invoice']

        invoices = Invoice.search([
            ('contract_id', 'in', self.ids),
            ('date_due', '<', fields.Date.today()),
        ])

        inv_dict = defaultdict(lambda: Invoice.browse())

        for inv in invoices:
            inv_dict[inv.contract_id.id] += inv

        for record in self:
            record.past_due_invoice_ids = \
                inv_dict.get(record.id, None)
