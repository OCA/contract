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
                contract_tmpl = line.product_id.contract_template_id
                contract = self.env['account.analytic.account'].create({
                    'name': '%s Contract' % rec.name,
                    'partner_id': rec.partner_id.id,
                    'contract_template_id': contract_tmpl.id,
                })
                line.contract_id = contract.id
                contract.recurring_create_invoice()
        return super(SaleOrder, self).action_confirm()
