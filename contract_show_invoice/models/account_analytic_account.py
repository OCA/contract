# -*- coding: utf-8 -*-
# © 2018 Alberto Martín Cortada - Guadaltech <alberto.martin@guadaltech.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_total_invoiced(self):
        invoice_line_model = self.env['account.invoice.line']
        for analytic in self:
            fetch_data = invoice_line_model.read_group(
                [('account_analytic_id', '=', analytic.id),
                 ('invoice_id.state', 'in', ['open', 'paid']),
                 ('invoice_id.type', 'in', ['out_invoice', 'out_refund'])],
                ['price_subtotal_signed'], [],
            )
            analytic.total_invoiced = fetch_data[0]['price_subtotal_signed']

    total_invoiced = fields.Float(string="Total Invoiced",
                                  compute='_compute_total_invoiced')
