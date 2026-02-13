# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _get_offset_kwargs(self):
        """Get offset kwargs, preferring line-level values over contract-level.

        Line-level offset takes precedence if:
        - invoicing_offset_value is non-zero, OR
        - invoicing_offset_type is not the default 'days'

        Otherwise falls back to contract-level offset.
        """
        self.ensure_one()

        # Check if line has its own offset set (non-default values)
        line_has_offset = (
            self.invoicing_offset_value != 0 or self.invoicing_offset_type != "days"
        )

        if line_has_offset:
            # Use line-level offset
            kwargs = {
                "invoicing_offset_type": self.invoicing_offset_type,
                "invoicing_offset_value": self.invoicing_offset_value,
            }
        else:
            # Fall back to contract-level offset
            kwargs = {
                "invoicing_offset_type": self.contract_id.invoicing_offset_type,
                "invoicing_offset_value": self.contract_id.invoicing_offset_value,
            }

        if hasattr(self.contract_id, "align_billing_cycle"):
            kwargs["align_billing_cycle"] = self.contract_id.align_billing_cycle

        return kwargs

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "contract_id.invoicing_offset_type",
        "contract_id.invoicing_offset_value",
        "invoicing_offset_type",
        "invoicing_offset_value",
        "recurring_next_date",
    )
    def _compute_next_period_date_end(self):
        for rec in self:
            kwargs = rec._get_offset_kwargs()

            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_invoice_date=rec.recurring_next_date,
                recurring_invoicing_type=rec.recurring_invoicing_type,
                recurring_invoicing_offset=rec.recurring_invoicing_offset,
                **kwargs,
            )

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "contract_id.invoicing_offset_type",
        "contract_id.invoicing_offset_value",
        "invoicing_offset_type",
        "invoicing_offset_value",
    )
    def _compute_recurring_next_date(self):
        for rec in self:
            kwargs = rec._get_offset_kwargs()

            rec.recurring_next_date = self.get_next_invoice_date(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                **kwargs,
            )

    @api.constrains("recurring_next_date", "date_start")
    def _check_recurring_next_date_start_date(self):
        # Filter out lines that have a negative offset (advance payment)
        # Check both line-level and contract-level offset
        lines_to_check = self.filtered(
            lambda line: (
                line.invoicing_offset_value >= 0
                and line.contract_id.invoicing_offset_value >= 0
            )
        )

        if lines_to_check:
            super(ContractLine, lines_to_check)._check_recurring_next_date_start_date()
        return

    @api.constrains("last_date_invoiced")
    def _check_last_date_invoiced(self):
        """Override to allow advance billing with negative offset.

        With advance billing (negative offset), the recurring_next_date can
        temporarily appear to be before last_date_invoiced during the invoice
        generation process. We skip this check for lines with negative offset.
        """
        # Filter out lines that have a negative offset (advance payment)
        lines_to_check = self.filtered(
            lambda line: (
                line.invoicing_offset_value >= 0
                and line.contract_id.invoicing_offset_value >= 0
            )
        )

        if lines_to_check:
            super(ContractLine, lines_to_check)._check_last_date_invoiced()
        return

    def _get_period_to_invoice(
        self, last_date_invoiced, recurring_next_date, stop_at_date_end=True
    ):
        """Get the period dates for invoicing.

        For advance billing (negative offset), the period is derived from
        recurring_next_date by reversing the offset. This correctly handles
        consecutive invoice cycles without cumulative drift.

        Example with offset = -1 months:
        - recurring_next_date = 2026-01-01 (trigger date)
        - Reverse offset: period_start = 2026-01-01 + 1 month = 2026-02-01
        - period_end = 2026-02-28
        - Invoice shows: Feb 1 - Feb 28 (invoiced in January)

        The base approach of shifting first_date_invoiced forward caused a
        cumulative shift bug: after the first invoice, last_date_invoiced
        already reflected the shifted period, so shifting again skipped months.
        """
        self.ensure_one()
        if not recurring_next_date:
            return False, False, False

        kwargs = self._get_offset_kwargs()
        offset_value = kwargs.get("invoicing_offset_value", 0)
        offset_type = kwargs.get("invoicing_offset_type", "days")

        if offset_value < 0:
            # For advance billing, derive the period from recurring_next_date.
            # get_next_invoice_date computes:
            #   invoice_date = period_start + days_offset + flexible_offset
            # Reversing to find period_start:
            #   period_start = invoice_date - flexible_offset - days_offset
            first_date_invoiced = recurring_next_date - relativedelta(
                **{offset_type: offset_value}
            )
            first_date_invoiced -= relativedelta(days=self.recurring_invoicing_offset)

            # Period end: simple forward calculation from derived period start
            last_date_invoiced = self.get_next_period_date_end(
                first_date_invoiced,
                self.recurring_rule_type,
                self.recurring_interval,
                max_date_end=(self.date_end if stop_at_date_end else False),
            )

            # If date_end clamped the period end before the start,
            # or get_next_period_date_end returned False (period start
            # past date_end), the contract has ended — nothing left to invoice.
            if not last_date_invoiced or last_date_invoiced < first_date_invoiced:
                return False, False, False
        else:
            # Standard billing: use base logic with reverse-offset
            first_date_invoiced = (
                last_date_invoiced + relativedelta(days=1)
                if last_date_invoiced
                else self.date_start
            )
            last_date_invoiced = self.get_next_period_date_end(
                first_date_invoiced,
                self.recurring_rule_type,
                self.recurring_interval,
                max_date_end=(self.date_end if stop_at_date_end else False),
                next_invoice_date=recurring_next_date,
                recurring_invoicing_type=self.recurring_invoicing_type,
                recurring_invoicing_offset=self.recurring_invoicing_offset,
                **kwargs,
            )

        return first_date_invoiced, last_date_invoiced, recurring_next_date
