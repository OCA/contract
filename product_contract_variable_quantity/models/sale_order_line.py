# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_type = fields.Selection(
        selection=[
            ("fixed", "Fixed quantity"),
            ("variable", "Variable quantity"),
        ],
        required=False,
        default="fixed",
        string="Qty. type",
    )
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula", string="Qty. formula"
    )

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        for rec in self:
            if rec.product_id.is_contract:
                rec.qty_type = rec.product_id.qty_type
                rec.qty_formula_id = rec.product_id.qty_formula_id
        return res

    def _prepare_contract_line_values(self, contract, predecessor_contract_line=False):
        values = super(SaleOrderLine, self)._prepare_contract_line_values(
            contract, predecessor_contract_line
        )
        values["qty_type"] = self.qty_type
        values["qty_formula_id"] = self.qty_formula_id.id
        return values
