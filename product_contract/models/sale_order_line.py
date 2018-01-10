# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract'
    )

    @api.multi
    def _get_create_contract_vals(self):
        """ Returns vals for creation of analytic account """
        self.ensure_one()
        order = self.order_id
        contract_template = self.product_id.contract_template_id
        vals = {
            'name': '%s Contract' % order.name,
            'partner_id': order.partner_id.id,
            'contract_template_id': contract_template.id,
        }
        return vals
