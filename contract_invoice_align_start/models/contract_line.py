# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from calendar import monthrange

from dateutil.relativedelta import relativedelta

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "contract_id.align_billing_cycle",
        "recurring_next_date",
    )
    def _compute_next_period_date_end(self):
        for rec in self:
            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_invoice_date=rec.recurring_next_date,
                recurring_invoicing_type=rec.recurring_invoicing_type,
                recurring_invoicing_offset=rec.recurring_invoicing_offset,
                align_billing_cycle=rec.contract_id.align_billing_cycle,
            )

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "contract_id.align_billing_cycle",
    )
    def _compute_recurring_next_date(self):
        for rec in self:
            rec.recurring_next_date = self.get_next_invoice_date(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                align_billing_cycle=rec.contract_id.align_billing_cycle,
            )

    @api.model
    def _compute_prorated(
        self,
        period_first_date,
        period_last_date,
        invoice_date,
        recurring_rule_type,
        recurring_interval,
        recurring_invoicing_type,
    ):
        """Override to return 1.0 for full calendar months.

        The base contract_variable_qty_prorated module calculates proration
        using a theoretical period based on invoice_date, which can give
        incorrect results for months with fewer days (e.g., February 28 days
        vs January 31 days gives 28/31 = 0.9).

        This override detects full calendar months (1st to last day of month)
        and returns 1.0 regardless of the theoretical calculation.
        """
        if not period_first_date or not period_last_date:
            return super()._compute_prorated(
                period_first_date,
                period_last_date,
                invoice_date,
                recurring_rule_type,
                recurring_interval,
                recurring_invoicing_type,
            )

        # Check if this is a full calendar month for monthly recurring
        if recurring_rule_type in ("monthly", "monthlylastday"):
            _, days_in_month = monthrange(
                period_first_date.year, period_first_date.month
            )

            is_full_month = (
                period_first_date.day == 1
                and period_last_date.day == days_in_month
                and period_first_date.month == period_last_date.month
                and period_first_date.year == period_last_date.year
            )

            if is_full_month:
                # Full month = no proration
                return 1.0

        # Fall back to base calculation for partial periods
        return super()._compute_prorated(
            period_first_date,
            period_last_date,
            invoice_date,
            recurring_rule_type,
            recurring_interval,
            recurring_invoicing_type,
        )

    def _get_period_to_invoice(
        self, last_date_invoiced, recurring_next_date, stop_at_date_end=True
    ):
        self.ensure_one()
        if not recurring_next_date:
            return False, False, False
        # Calculate First Date Invoiced
        first_date_invoiced = (
            last_date_invoiced + relativedelta(days=1)
            if last_date_invoiced
            else self.date_start
        )

        # Calculate Last Date Invoiced (Period End)
        last_date_invoiced = self.get_next_period_date_end(
            first_date_invoiced,
            self.recurring_rule_type,
            self.recurring_interval,
            max_date_end=(self.date_end if stop_at_date_end else False),
            next_invoice_date=recurring_next_date,
            recurring_invoicing_type=self.recurring_invoicing_type,
            recurring_invoicing_offset=self.recurring_invoicing_offset,
            align_billing_cycle=self.contract_id.align_billing_cycle,
        )
        return first_date_invoiced, last_date_invoiced, recurring_next_date

    def _prepare_invoice_line(self):
        """Override to implement proration if alignment is active.

        Pro-rata is ONLY applied when:
        1. align_billing_cycle is True
        2. The period is a PARTIAL month (not starting on 1st or not ending on last day)

        Full months (e.g., Feb 1-28, Mar 1-31) are always billed at qty=1.0
        regardless of how many days are in the month.

        IMPORTANT: We use _get_period_to_invoice() to get the actual period dates,
        NOT the computed fields (next_period_date_start/end). This ensures
        consistency with the invoice description dates, especially when using
        invoice offset (advance billing).
        """
        self.ensure_one()
        res = super()._prepare_invoice_line()

        # Skip if line should not be invoiced (res is False or empty dict)
        if not res:
            return res

        # Check if proration is needed
        if (
            self.contract_id.align_billing_cycle
            and self.recurring_rule_type == "monthly"
        ):
            # Get the ACTUAL period being invoiced (same as invoice description)
            # This is critical for advance billing where computed fields may differ
            dates = self._get_period_to_invoice(
                self.last_date_invoiced, self.recurring_next_date
            )
            period_start = dates[0]
            period_end = dates[1]

            if period_start and period_end:
                _, days_in_month = monthrange(period_start.year, period_start.month)

                # Check if this is a FULL month (1st to last day of same month)
                is_full_month = (
                    period_start.day == 1
                    and period_end.day == days_in_month
                    and period_start.month == period_end.month
                    and period_start.year == period_end.year
                )

                # Only pro-rate PARTIAL months (first invoice to align billing)
                if not is_full_month:
                    actual_days = (period_end - period_start).days + 1
                    if actual_days < days_in_month:
                        ratio = actual_days / days_in_month
                        current_qty = res.get("quantity") or self.quantity or 1.0
                        new_qty = current_qty * ratio
                        description = res.get("name", "")
                        description += (
                            f" (Prorated: {actual_days}/{days_in_month} days)"
                        )
                        res.update({"quantity": new_qty, "name": description})

        return res
