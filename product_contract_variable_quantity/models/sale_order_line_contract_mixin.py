# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrderLineContractMixin(models.AbstractModel):
    _inherit = "sale.order.line.contract.mixin"

    qty_type = fields.Selection(
        selection=[
            ("fixed", "Fixed quantity"),
            ("variable", "Variable quantity"),
        ],
        required=False,
        default="fixed",
        string="Qty. type",
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula",
        string="Qty. formula",
        compute="_compute_qty_formula_id",
        precompute=True,
        store=True,
        readonly=False,
    )

    @api.depends("product_id")
    def _compute_product_contract_data(self):
        res = super()._compute_product_contract_data()
        for rec in self:
            if rec.product_id.is_contract:
                rec.qty_type = rec.product_id.qty_type or "fixed"
        return res

    @api.depends("qty_type")
    def _compute_qty_formula_id(self):
        for rec in self:
            if rec.qty_type == "variable":
                rec.qty_formula_id = rec.product_id.qty_formula_id
            else:
                rec.qty_formula_id = False
