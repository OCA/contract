# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    def _get_offset_kwargs(self):
        """Return the extra arguments for the recurrence helper methods.

        Meant as an extension point for modules that need to pass extra
        arguments down to ``get_next_invoice_date`` and
        ``get_next_period_date_end``.
        """
        self.ensure_one()
        return {
            "invoicing_offset_type": self.invoicing_offset_type,
            "invoicing_offset_value": self.invoicing_offset_value,
        }

    @api.model
    def get_next_invoice_date(
        self,
        next_period_date_start,
        recurring_invoicing_type,
        recurring_invoicing_offset,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        invoicing_offset_type="daily",
        invoicing_offset_value=0,
        **kwargs,
    ):
        """Shift the standard next invoice date by the flexible offset."""
        next_invoice_date = super().get_next_invoice_date(
            next_period_date_start,
            recurring_invoicing_type,
            recurring_invoicing_offset,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
            **kwargs,
        )
        if not next_invoice_date or not invoicing_offset_value:
            return next_invoice_date
        return next_invoice_date + self.get_relative_delta(
            invoicing_offset_type, invoicing_offset_value
        )

    @api.model
    def get_next_period_date_end(
        self,
        next_period_date_start,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        next_invoice_date=False,
        recurring_invoicing_type=False,
        recurring_invoicing_offset=False,
        invoicing_offset_type="daily",
        invoicing_offset_value=0,
        **kwargs,
    ):
        """Reverse the flexible offset before the standard back-calculation."""
        if next_invoice_date and invoicing_offset_value:
            next_invoice_date -= self.get_relative_delta(
                invoicing_offset_type, invoicing_offset_value
            )
        return super().get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
            next_invoice_date=next_invoice_date,
            recurring_invoicing_type=recurring_invoicing_type,
            recurring_invoicing_offset=recurring_invoicing_offset,
            **kwargs,
        )
