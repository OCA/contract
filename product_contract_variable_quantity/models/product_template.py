# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_type = fields.Selection(
        selection=[
            ("fixed", "Fixed quantity"),
            ("variable", "Variable quantity"),
        ],
        required=False,
        default="fixed",
        string="Qty. type",
        compute="_compute_qty_type",
        store=True,
        readonly=False,
    )
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula",
        string="Qty. formula",
        compute="_compute_qty_type",
        store=True,
        readonly=False,
    )

    @api.depends("is_contract")
    def _compute_qty_type(self):
        self.filtered(lambda rec: not rec.is_contract).qty_type = False
        self.filtered(
            lambda rec: not rec.qty_type or rec.qty_type == "fixed"
        ).qty_formula_id = False
