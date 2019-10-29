# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    @api.multi
    def action_show_contract_forecast(self):
        self.ensure_one()
        context = {'search_default_groupby_date_invoice': True}
        context.update(self.env.context)

        return {
            "type": "ir.actions.act_window",
            "name": _("Contract Forecast"),
            "res_model": "contract.line.forecast.period",
            "domain": [("contract_id", "=", self.id)],
            "view_mode": "pivot,tree",
            "context": context,
        }

    @api.model
    def _get_forecast_update_trigger_fields(self):
        return []

    @api.multi
    def write(self, values):
        res = super(ContractContract, self).write(values)
        if any(
                [
                    field in values
                    for field in self._get_forecast_update_trigger_fields()
                ]
        ):
            for rec in self:
                for contract_line in rec.contract_line_ids:
                    contract_line.with_delay()._generate_forecast_periods()
        return res
