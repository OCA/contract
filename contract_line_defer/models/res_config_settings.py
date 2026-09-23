# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    defer_contract_line_start = fields.Boolean(
        related="company_id.defer_contract_line_start",
        readonly=False,
    )
