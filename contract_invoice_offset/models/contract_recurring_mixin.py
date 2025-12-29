# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractRecurringMixin(models.AbstractModel):
    _inherit = "contract.recurring.mixin"

    invoicing_offset_type = fields.Selection(
        [
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        default="days",
        required=True,
    )
    invoicing_offset_value = fields.Integer(
        default=0,
        help="Positive value delays invoice, negative value invoices in advance. "
        "E.g., -1 for 1 month in advance.",
    )

    @api.model
    def get_next_invoice_date(
        self,
        next_period_date_start,
        recurring_invoicing_type,
        recurring_invoicing_offset,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        invoicing_offset_type="days",
        invoicing_offset_value=0,
        **kwargs,
    ):
        """Compute the date of the next invoice based on all parameters,
        including flexible offsets.
        """
        next_period_date_end = self.get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end=max_date_end,
            invoicing_offset_type=invoicing_offset_type,
            invoicing_offset_value=invoicing_offset_value,
            **kwargs,
        )
        if not next_period_date_end:
            return False

        # Calculate base date
        if recurring_invoicing_type == "pre-paid":
            base_date = next_period_date_start
        else:
            base_date = next_period_date_end

        # Apply offset
        # First, apply the original days-based offset for consistency.
        base_date += relativedelta(days=recurring_invoicing_offset)
        # Then, apply the new flexible offset.
        if invoicing_offset_type == "days":
            return base_date + relativedelta(days=invoicing_offset_value)
        elif invoicing_offset_type == "weeks":
            return base_date + relativedelta(weeks=invoicing_offset_value)
        elif invoicing_offset_type == "months":
            return base_date + relativedelta(months=invoicing_offset_value)
        elif invoicing_offset_type == "years":
            return base_date + relativedelta(years=invoicing_offset_value)

        return base_date

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
        invoicing_offset_type="days",
        invoicing_offset_value=0,
        **kwargs,
    ):
        """Compute the end date for the next period, supporting flexible
        reverse calculation."""
        if not next_period_date_start or (
            max_date_end and next_period_date_start > max_date_end
        ):
            return False

        # Check for billing cycle alignment from contract_invoice_align_start
        align_billing_cycle = kwargs.get("align_billing_cycle")
        if align_billing_cycle and next_period_date_start.day != 1:
            # Force end to be end of the current month (alignment takes precedence)
            next_period_date_end = next_period_date_start + relativedelta(day=31)
            if max_date_end and next_period_date_end > max_date_end:
                next_period_date_end = max_date_end
            return next_period_date_end

        if not next_invoice_date:
            # Regular case: use relative delta (unchanged from base)
            next_period_date_end = (
                next_period_date_start
                + self.get_relative_delta(recurring_rule_type, recurring_interval)
                - relativedelta(days=1)
            )
        else:
            # Forced invoice date: back-calculate period end
            # We need to reverse the offset to find the base date (start or end)

            # 1. Reverse the offset to get the 'base date' (which is start or end)
            base_date = next_invoice_date
            # First, reverse the new flexible offset.
            if invoicing_offset_type == "days":
                base_date -= relativedelta(days=invoicing_offset_value)
            elif invoicing_offset_type == "weeks":
                base_date -= relativedelta(weeks=invoicing_offset_value)
            elif invoicing_offset_type == "months":
                base_date -= relativedelta(months=invoicing_offset_value)
            elif invoicing_offset_type == "years":
                base_date -= relativedelta(years=invoicing_offset_value)
            # Then, reverse the original days-based offset.
            base_date -= relativedelta(days=recurring_invoicing_offset)

            # 2. From base date, derive period end.
            if recurring_invoicing_type == "pre-paid":
                # base_date is Start Date
                # End Date = Start Date + Duration - 1 day
                next_period_date_end = (
                    base_date
                    + self.get_relative_delta(recurring_rule_type, recurring_interval)
                    - relativedelta(days=1)
                )
            else:  # post-paid
                # base_date is End Date
                next_period_date_end = base_date

        if max_date_end and next_period_date_end > max_date_end:
            next_period_date_end = max_date_end
        return next_period_date_end
