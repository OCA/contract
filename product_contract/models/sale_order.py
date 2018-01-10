# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """ If we have a contract in the order, set it up """
        for rec in self:
            order_lines = self.mapped('order_line').filtered(
                lambda r: r.product_id.is_contract
            )
            for line in order_lines:
                AnalyticAccount = self.env['account.analytic.account']
                contract = AnalyticAccount.create(
                    line._get_create_contract_vals(),
                )
                line.contract_id = contract.id
                contract.recurring_create_invoice()
        return super(SaleOrder, self).action_confirm()
