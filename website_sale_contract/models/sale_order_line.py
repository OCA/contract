# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def _get_create_contract_vals(self):
        vals = super(SaleOrderLine, self)._get_create_contract_vals()
        temp_contract = self.env['contract.temp'].search([
            ('order_line_id', '=', self.id),
        ])
        if temp_contract:
            vals.update({
                'customer_signature': temp_contract.signature_image,
                'signature_name': temp_contract.signatory_name,
            })
        return vals
