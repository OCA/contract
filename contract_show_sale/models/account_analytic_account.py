# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _get_total_sale(self):
        sale_model = self.env['sale.order']
        for analytic in self:
            fetch_data = sale_model.read_group(
                [('project_id', '=', analytic.id),
                 ('state', 'not in', ['draft', 'sent', 'cancel'])],
                ['amount_untaxed'], [],
            )
            analytic.total_sale = fetch_data[0]['amount_untaxed']

    total_sale = fields.Float(string="Total Sales",
                              compute='_get_total_sale')
