# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.fields import first


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends("partner_shipping_id", "order_line.contract_line_id")
    def _compute_delivery_zone_id(self):
        # Get sale orders with contracts and a delivery zone on it
        contract_sales = self.filtered(
            lambda sale: any(
                line.contract_line_id.contract_id.partner_delivery_zone_id
                for line in sale.order_line
            )
        )
        for sale in contract_sales:
            delivery_zone = first(
                sale.mapped(
                    "order_line.contract_line_id.contract_id.partner_delivery_zone_id"
                )
            )
            sale.delivery_zone_id = delivery_zone
        # Fallback to normal sale orders
        return super(SaleOrder, (self - contract_sales))._compute_delivery_zone_id()
