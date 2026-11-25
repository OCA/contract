# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_discount_per_contract_line = fields.Boolean(
        string="Discounts on contract lines",
        implied_group="contract.group_discount_per_contract_line",
        help="Show a discount column on contract and contract template lines.",
    )
