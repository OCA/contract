# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    contract_tag_ids = fields.Many2many(
        comodel_name="contract.tag",
        relation="stock_picking_contract_tag_rel",
        column1="picking_id",
        column2="tag_id",
    )
