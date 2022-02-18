# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """Adds the picking order if present in procurement group to
        transmit to the picking.

        :return: _description_
        :rtype: _type_
        """
        res = super()._get_new_picking_values()
        contract_tags = self.mapped("group_id.sale_id.contract_tag_ids")
        if contract_tags:
            res.update(
                {
                    "contract_tag_ids": [
                        (4, contract_tag.id) for contract_tag in contract_tags
                    ]
                }
            )
        return res
