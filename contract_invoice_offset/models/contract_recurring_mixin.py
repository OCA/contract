# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractRecurringMixin(models.AbstractModel):
    _inherit = "contract.recurring.mixin"

    invoicing_offset_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("yearly", "Year(s)"),
        ],
        default="daily",
        string="Invoicing offset unit",
        required=True,
        help="Unit the invoicing offset value is expressed in.",
    )
    invoicing_offset_value = fields.Integer(
        default=0,
        string="Invoicing offset value",
        help="Positive value delays the invoice, negative value invoices in "
        "advance. E.g. -1 combined with the Month(s) unit invoices one month "
        "in advance.",
    )

    def _get_invoicing_offset_relative_delta(self):
        if not (self.invoicing_offset_type and self.invoicing_offset_value):
            return False
        return self.get_relative_delta(
            self.invoicing_offset_type, self.invoicing_offset_value
        )

    def get_next_invoice_date(
        self,
        next_period_date_start=None,
        recurring_invoicing_type=None,
        recurring_invoicing_offset=None,
        recurring_rule_type=None,
        recurring_interval=None,
        max_date_end=None,
    ):
        next_invoice_date = super().get_next_invoice_date(
            next_period_date_start,
            recurring_invoicing_type,
            recurring_invoicing_offset,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
        )
        invoicing_offset_delta = self._get_invoicing_offset_relative_delta()
        if next_invoice_date and invoicing_offset_delta:
            return next_invoice_date + invoicing_offset_delta
        return next_invoice_date

    def get_next_period_date_end(
        self,
        next_period_date_start=None,
        recurring_rule_type=None,
        recurring_interval=None,
        max_date_end=None,
        next_invoice_date=False,
        recurring_invoicing_type=False,
        recurring_invoicing_offset=False,
    ):
        """Reverse the flexible offset before the standard back-calculation."""
        invoicing_offset_delta = self._get_invoicing_offset_relative_delta()
        if next_invoice_date and invoicing_offset_delta:
            next_invoice_date -= invoicing_offset_delta
        return super().get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
            next_invoice_date=next_invoice_date,
            recurring_invoicing_type=recurring_invoicing_type,
            recurring_invoicing_offset=recurring_invoicing_offset,
        )
