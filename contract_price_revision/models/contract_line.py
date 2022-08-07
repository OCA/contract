# Copyright 2019 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    previous_price = fields.Float(
        string="Previous price",
        related="predecessor_contract_line_id.price_unit",
        readonly=True,
    )
    variation_percent = fields.Float(
        compute="_compute_variation_percent",
        store=True,
        digits="Product Price",
        string="Variation %",
    )

    @api.depends("price_unit", "predecessor_contract_line_id.price_unit")
    def _compute_variation_percent(self):
        for line in self:
            if line.price_unit and line.previous_price:
                line.variation_percent = (
                    line.price_unit / line.previous_price - 1
                ) * 100
            else:
                line.variation_percent = 0.0
