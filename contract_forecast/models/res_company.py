# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    contract_forecast_interval = fields.Integer(
        string="Number of contract forecast Periods", default=12
    )
    contract_forecast_rule_type = fields.Selection(
        [("monthly", "Month(s)"), ("yearly", "Year(s)")], default="monthly"
    )
