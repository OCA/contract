# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.depends("contract_line_ids.is_deferred")
    def _compute_recurring_next_date(self):
        """
        Add depends is_deferred
        """
        return super()._compute_recurring_next_date()
