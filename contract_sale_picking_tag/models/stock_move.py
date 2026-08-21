# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """Adds the picking order if present in procurement group to
        transmit to the picking.

        :return: _description_
        :rtype: _type_
        """
        res = super()._get_new_picking_values()
        contract_tags = self.sale_line_id.order_id.contract_tag_ids
        if contract_tags:
            res["contract_tag_ids"] = [Command.link(tag.id) for tag in contract_tags]
        return res
