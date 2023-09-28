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

    never_revise_price = fields.Boolean(
        help="Check this if you don't want to allow price revision."
    )
    price_can_be_revised = fields.Boolean(
        compute="_compute_price_can_be_revised",
        help="Technical field in order to know if the line price can be revised.",
    )

    @api.depends_context("date_start")
    def _compute_price_can_be_revised(self):
        date_start = self.env.context.get("date_start", fields.Date.today())
        lines_can_be_revised = self.filtered(
            lambda line: not line.never_revise_price
            and not line.automatic_price
            and not line.successor_contract_line_id
            and line.recurring_next_date
            and not line.display_type
            and (not line.date_end or line.date_end >= date_start)
        )
        lines_can_be_revised.price_can_be_revised = True
        (self - lines_can_be_revised).price_can_be_revised = False

    @api.depends("price_unit", "predecessor_contract_line_id.price_unit")
    def _compute_variation_percent(self):
        for line in self:
            if line.price_unit and line.previous_price:
                line.variation_percent = (
                    line.price_unit / line.previous_price - 1
                ) * 100
            else:
                line.variation_percent = 0.0

    def _prepare_value_for_plan_successor_price(
        self, date_start, date_end, is_auto_renew, price, recurring_next_date=False
    ):
        """
        Override contract function to prepare values for new contract line
        adding the new price as parameter
        """
        res = super()._prepare_value_for_plan_successor(
            date_start, date_end, is_auto_renew, recurring_next_date=recurring_next_date
        )
        res.update({"price_unit": price})
        return res
