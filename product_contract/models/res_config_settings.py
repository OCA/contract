# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    create_contract_at_sale_order_confirmation = fields.Boolean(
        related="company_id.create_contract_at_sale_order_confirmation", readonly=False
    )
