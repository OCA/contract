# -*- coding: utf-8 -*-
# © 2018 Alberto Martín Cortada - Guadaltech <alberto.martin@guadaltech.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_total_invoiced(self):
        for analytic in self:
            invoices = self.env['account.invoice'].search(
                [('invoice_line_ids.account_analytic_id', '=', analytic.id)])
            analytic.total_invoiced = sum(invoices.mapped('amount_total'))

    total_invoiced = fields.Float(string="Total Invoiced",
                                  compute='_compute_total_invoiced')

