# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_contract_line_refund_on_stop = fields.Boolean(
        related="company_id.enable_contract_line_refund_on_stop", readonly=False
    )
