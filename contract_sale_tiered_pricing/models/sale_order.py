# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order"

    def recompute_contract_cumulated_qty(self):
        draft_orders = self.filtered(lambda s: s.state in ["draft", "sent"])
        lines = draft_orders.mapped("order_line").filtered("product_id")
        lines._compute_contract_cumulated_qty()
        lines.recompute_price_and_description()
