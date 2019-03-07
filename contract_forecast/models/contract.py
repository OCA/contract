# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountAnalyticAccount(models.Model):

    _inherit = "account.analytic.account"

    @api.multi
    def action_show_contract_forecast(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Contract Forecast"),
            "res_model": "contract.line.forecast.period",
            "domain": [("contract_id", "=", self.id)],
            "view_mode": "pivot,tree",
            "context": self.env.context,
        }
