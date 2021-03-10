# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    specific_contract_payment_mode = fields.Boolean(
        related="company_id.specific_contract_payment_mode",
        string="Specific payment mode for contracts created from sale orders",
        readonly=False
    )
