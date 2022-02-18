# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    contract_tag_ids = fields.Many2many(
        comodel_name="contract.tag",
        relation="sale_order_contract_tag_rel",
        column1="order_id",
        column2="tag_id",
        string="Contract tags",
    )
