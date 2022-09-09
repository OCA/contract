# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    invoicing_sales = fields.Boolean(
        string='Invoice Pending Sales Orders',
        help='If checked include sales with same analytic account to invoice '
             'in contract invoice creation.',
    )

    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        invoices = super()._recurring_create_invoice(date_ref)
        if not self.invoicing_sales:
            return invoices
        sales = self.env['sale.order'].search([
            ('analytic_account_id', '=', self.group_id.id),
            ('partner_invoice_id', 'child_of',
             self.partner_id.commercial_partner_id.ids),
            ('invoice_status', '=', 'to invoice'),
            ('date_order', '<=',
             '{} 23:59:59'.format(self.recurring_next_date)),
        ])
        if sales:
            invoice_ids = sales.action_invoice_create()
            invoices |= self.env['account.invoice'].browse(invoice_ids)[:1]
