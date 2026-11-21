# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _get_offset_kwargs(self):
        """Prefer the line level offset over the contract level one.

        The line level offset takes precedence as soon as it differs from the
        field defaults, otherwise the contract level offset applies.
        """
        self.ensure_one()
        line_has_offset = (
            self.invoicing_offset_value != 0 or self.invoicing_offset_type != "daily"
        )
        if line_has_offset:
            kwargs = super()._get_offset_kwargs()
        else:
            kwargs = self.contract_id._get_offset_kwargs()
        # The billing cycle alignment is always a contract level setting.
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
        "contract_id.align_billing_cycle",
        "recurring_next_date",
    )
    def _compute_next_period_date_end(self):
        """Overwrite to pass the offset settings down to the helper method."""
        for rec in self:
            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_invoice_date=rec.recurring_next_date,
                recurring_invoicing_type=rec.recurring_invoicing_type,
                recurring_invoicing_offset=rec.recurring_invoicing_offset,
                **rec._get_offset_kwargs(),
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
        "contract_id.align_billing_cycle",
    )
    def _compute_recurring_next_date(self):
        """Overwrite to pass the offset settings down to the helper method."""
        for rec in self:
            rec.recurring_next_date = self.get_next_invoice_date(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                **rec._get_offset_kwargs(),
            )

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
        self, last_date_invoiced, recurring_next_date, stop_at_date_end=True
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
        if not recurring_next_date:
            return False, False, False
        kwargs = self._get_offset_kwargs()

        if kwargs["invoicing_offset_value"] < 0:
            # get_next_invoice_date computes
            # ``invoice_date = period_start + days_offset + flexible_offset``,
            # so reverse both offsets to get back to the period start.
            first_date_invoiced = recurring_next_date - self.get_relative_delta(
                kwargs["invoicing_offset_type"], kwargs["invoicing_offset_value"]
            )
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

        # Standard billing: base logic, reversing the flexible offset when
        # back-calculating the period end from the forced invoice date.
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
