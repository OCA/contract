# Copyright 2024 ASCONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    contract_line_id = fields.Many2one(
        related="project_id.contract_line_id",
    )

    @api.depends("contract_line_id.product_id", "amount")
    def _compute_timesheet_invoice_type(self):  # pylint: disable=missing-return
        super()._compute_timesheet_invoice_type()
        for rec in self:
            if rec.so_line:
                # billed via the sale order
                continue
            if not rec.contract_line_id:
                # no contract, let the default algo do it's job
                continue
            # From here, similar algorithm as in sale_timesheet
            product_id = rec.contract_line_id.product_id
            if product_id.type != "service":
                continue
            if product_id.invoice_policy == "delivery":
                service_type = product_id.service_type
                if service_type == "timesheet":
                    rec.timesheet_invoice_type = (
                        "timesheet_revenues" if rec.amount > 0 else "billable_time"
                    )
                else:
                    rec.timesheet_invoice_type = (
                        f"billable_{service_type}"
                        if service_type in ["milestones", "manual"]
                        else "billable_fixed"
                    )
            elif product_id.invoice_policy == "order":
                rec.timesheet_invoice_type = "billable_fixed"
