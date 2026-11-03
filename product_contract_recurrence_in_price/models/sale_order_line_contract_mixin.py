# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLineContractMixin(models.AbstractModel):
    _inherit = "sale.order.line.contract.mixin"

    include_recurrence_in_price = fields.Boolean(
        help="The amounts of the Sale Order Line will be multiplied"
        "by the number of times the line will be invoiced.",
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
    recurring_invoicing_number = fields.Float(
        compute="_compute_recurring_invoice_number",
        digits=(16, 1),
        help="Number of times a line will be invoiced.",
        store=True,
        readonly=False,
        precompute=True,
    )

    @api.depends("product_id")
    def _compute_product_contract_data(self):
        res = super()._compute_product_contract_data()
        for rec in self:
            rec.include_recurrence_in_price = (
                rec.product_id.is_contract
                and rec.product_id.include_recurrence_in_price
            )
        return res

    @api.depends("date_start", "date_end", "recurring_interval", "recurring_rule_type")
    def _compute_recurring_invoice_number(self):
        for rec in self:
            if (
                not rec.date_start
                or not rec.date_end
                or not rec.recurring_interval
                or not rec.recurring_rule_type
            ):
                rec.recurring_invoicing_number = 0
                continue
            days_total = (rec.date_end - rec.date_start).days
            if rec.recurring_rule_type == "daily":
                interval_number = days_total
            elif rec.recurring_rule_type == "weekly":
                interval_number = days_total / 7
            elif rec.recurring_rule_type in ("monthly", "monthlylastday"):
                interval_number = days_total / (365.25 / 12)
            elif rec.recurring_rule_type == "quarterly":
                interval_number = days_total / (365.25 / 4)
            elif rec.recurring_rule_type == "semesterly":
                interval_number = days_total / (365.25 / 2)
            elif rec.recurring_rule_type == "yearly":
                interval_number = days_total / 365.25
            else:
                raise ValidationError(_("Invalid recurring_rule_type."))
            rec.recurring_invoicing_number = interval_number / rec.recurring_interval
