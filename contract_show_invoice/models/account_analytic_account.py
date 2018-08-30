# -*- coding: utf-8 -*-
# © 2018 Alberto Martín Cortada - Guadaltech <alberto.martin@guadaltech.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_total_invoiced(self):
        invoice_model = self.env['account.invoice']
        for analytic in self:
            fetch_data = invoice_model.read_group(
                [('invoice_line_ids.account_analytic_id', '=', analytic.id)],
                ['amount_total'], [],
            )
            analytic.total_invoiced = fetch_data[0]['amount_total']

    total_invoiced = fields.Float(string="Total Invoiced",
                                  compute='_compute_total_invoiced')
