# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    enable_contract_forecast = fields.Boolean(
        string="Enable contract forecast",
        default=True,
        readonly=False,
        related="company_id.enable_contract_forecast",
    )
    contract_forecast_interval = fields.Integer(
        string="Number of contract forecast Periods",
        default=12,
        related="company_id.contract_forecast_interval",
        readonly=False,

    )
    contract_forecast_rule_type = fields.Selection(
        [("monthly", "Month(s)"), ("yearly", "Year(s)")],
        default="monthly",
        related="company_id.contract_forecast_rule_type",
        readonly=False,
    )
