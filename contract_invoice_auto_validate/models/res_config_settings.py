# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_post_contract_invoice = fields.Boolean(
        related="company_id.auto_post_contract_invoice", readonly=False
    )
