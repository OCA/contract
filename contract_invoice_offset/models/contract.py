# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.depends(
        "invoicing_offset_type",
        "invoicing_offset_value",
    )
    def _compute_recurring_next_date(self):
        return super()._compute_recurring_next_date()

    @api.depends(
        "invoicing_offset_type",
        "invoicing_offset_value",
    )
    def _compute_next_period_date_end(self):
        return super()._compute_next_period_date_end()
