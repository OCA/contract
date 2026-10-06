# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    @api.depends(
        "contract_id.invoicing_offset_type",
        "contract_id.invoicing_offset_value",
        "invoicing_offset_type",
        "invoicing_offset_value",
    )
    def _compute_next_period_date_end(self):
        return super()._compute_next_period_date_end()

    @api.depends(
        "contract_id.invoicing_offset_type",
        "contract_id.invoicing_offset_value",
        "invoicing_offset_type",
        "invoicing_offset_value",
    )
    def _compute_recurring_next_date(self):
        return super()._compute_recurring_next_date()

    def _get_invoicing_offset_relative_delta(self):
        res = super()._get_invoicing_offset_relative_delta()
        if not res and self.contract_id:
            return self.contract_id._get_invoicing_offset_relative_delta()
        return res

    def _is_advance_billed(self):
        """Return the lines invoiced ahead of the period they cover."""
        return self.filtered(
            lambda line: line.invoicing_offset_value < 0
            or line.contract_id.invoicing_offset_value < 0
        )

    @api.constrains("recurring_next_date", "date_start")
    def _check_recurring_next_date_start_date(self):
        # With advance billing the next invoice date legitimately precedes the
        # start of the period it covers, so the base check does not apply.
        return super(
            ContractLine, self - self._is_advance_billed()
        )._check_recurring_next_date_start_date()

    @api.constrains(
        "date_start", "date_end", "last_date_invoiced", "recurring_next_date"
    )
    def _check_last_date_invoiced(self):
        # With advance billing, recurring_next_date can temporarily appear to
        # be before last_date_invoiced while the invoice is generated, so the
        # base check does not apply.
        return super(
            ContractLine, self - self._is_advance_billed()
        )._check_last_date_invoiced()

    def _get_period_to_invoice(
        self, last_date_invoiced=None, recurring_next_date=None, stop_at_date_end=True
    ):
        """Get the period dates for invoicing.

        For advance billing (negative offset), the period is derived from
        recurring_next_date by reversing the offset. This correctly handles
        consecutive invoice cycles without cumulative drift.

        Example with an offset of -1 month:

        - recurring_next_date = 2026-01-01 (trigger date)
        - Reverse offset: period_start = 2026-01-01 + 1 month = 2026-02-01
        - period_end = 2026-02-28
        - Invoice shows: Feb 1 - Feb 28 (invoiced in January)

        The base approach of shifting first_date_invoiced forward caused a
        cumulative shift bug: after the first invoice, last_date_invoiced
        already reflected the shifted period, so shifting again skipped months.
        """
        self.ensure_one()
        if last_date_invoiced is None:
            last_date_invoiced = self.last_date_invoiced
        if recurring_next_date is None:
            recurring_next_date = self.recurring_next_date
        if not recurring_next_date:
            return False, False, False

        invoicing_offset_delta = self._get_invoicing_offset_relative_delta()
        if invoicing_offset_delta:
            # get_next_invoice_date computes
            # ``invoice_date = period_start + days_offset + flexible_offset``,
            # so reverse both offsets to get back to the period start.
            first_date_invoiced = recurring_next_date - invoicing_offset_delta
            first_date_invoiced -= relativedelta(days=self.recurring_invoicing_offset)

            # Period end: simple forward calculation from the derived start
            last_date_invoiced = self.get_next_period_date_end(
                first_date_invoiced,
                self.recurring_rule_type,
                self.recurring_interval,
                max_date_end=(self.date_end if stop_at_date_end else False),
            )

            # If date_end clamped the period end before the start, or
            # get_next_period_date_end returned False (period start past
            # date_end), the contract has ended: nothing left to invoice.
            if not last_date_invoiced or last_date_invoiced < first_date_invoiced:
                return False, False, False
            return first_date_invoiced, last_date_invoiced, recurring_next_date

        return super()._get_period_to_invoice(
            last_date_invoiced=last_date_invoiced,
            recurring_next_date=recurring_next_date,
            stop_at_date_end=stop_at_date_end,
        )
