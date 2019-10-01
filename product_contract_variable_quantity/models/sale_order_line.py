# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed quantity'),
            ('variable', 'Variable quantity'),
        ],
        required=False,
        default='fixed',
        string="Qty. type",
    )
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula", string="Qty. formula"
    )

    @api.onchange('product_id')
    def onchange_product(self):
        res = super(SaleOrderLine, self).onchange_product()
        for rec in self:
            if rec.product_id.is_contract:
                rec.qty_type = rec.product_id.qty_type
                rec.qty_formula_id = rec.product_id.qty_formula_id
        return res

    @api.multi
    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line=False
    ):
        values = super(SaleOrderLine, self)._prepare_contract_line_values(
            contract, predecessor_contract_line
        )
        values['qty_type'] = self.qty_type
        values['qty_formula_id'] = self.qty_formula_id.id
        return values
