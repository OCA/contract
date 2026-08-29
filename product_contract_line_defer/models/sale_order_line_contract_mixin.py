# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLineContractMixin(models.AbstractModel):
    _inherit = "sale.order.line.contract.mixin"

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

    @api.depends("product_id")
    def _compute_product_contract_data(self):
        res = super()._compute_product_contract_data()
        self.filtered(
            lambda line: line.product_id.is_contract and line.product_id.is_deferred
        ).update({"is_deferred": True})
        return res

    @api.depends(
        "product_id",
        "contract_start_date_method",
        "date_start",
        "date_end",
        "recurring_rule_type",
        "recurrence_interval",
        "recurring_invoicing_type",
        "is_deferred",
    )
    def _compute_name(self):
        """
        Trigger _compute_name if changes are done in product configurator
        """
        return super()._compute_name()
