# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    @api.depends("is_deferred")
    def _compute_allowed(self):
        res = super()._compute_allowed()
        for line in self:
            if line.is_deferred:
                line.update(
                    {
                        "is_plan_successor_allowed": False,
                        "is_stop_plan_successor_allowed": False,
                        "is_stop_allowed": False,
                        "is_cancel_allowed": False,
                        "is_un_cancel_allowed": False,
                    }
                )
        return res
