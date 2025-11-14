# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractRecurringMixin(models.AbstractModel):
    _inherit = "contract.recurring.mixin"

    is_deferred = fields.Boolean(
        "Deferred", help="Do not invoice this line until it is activated"
    )

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if "is_deferred" in fields:
            company = (
                self.env["res.company"].browse(company_id)
                if (company_id := result.get("company_id"))
                else self.env.company
            )
            if company.defer_contract_line_start:
                result["is_deferred"] = True
        return result

    def enable_deferred(self):
        self.ensure_one()
        self.is_deferred = True

    @api.depends(
        "is_deferred",
    )
    def _compute_recurring_next_date(self):
        """No next invoice date for deferred lines"""
        res = super()._compute_recurring_next_date()
        self.filtered(lambda r: r.is_deferred).update({"recurring_next_date": False})
        return res
