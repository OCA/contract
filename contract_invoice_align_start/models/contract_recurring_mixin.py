# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ContractRecurringMixin(models.AbstractModel):
    _inherit = "contract.recurring.mixin"

    align_billing_cycle = fields.Boolean(
        string="Align Billing Cycle to First Day of Month",
        help="If checked, the first invoicing period will be shortened to end on the "
        "last day of the month of the start date. Subsequent periods will follow "
        "the standard recurring rule (e.g., monthly starting from the 1st).",
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
        **kwargs,
    ):
        """Override to pass extra arguments through the computation chain.

        We reimplement the logic here because the base method does not support passing
        **kwargs to get_next_period_date_end, which causes our 'align_billing_cycle'
        parameter to be lost if we just call super().
        """
        next_period_date_end = self.get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
            recurring_invoicing_type=recurring_invoicing_type,
            recurring_invoicing_offset=recurring_invoicing_offset,
            **kwargs,
        )
        if not next_period_date_end:
            return False

        if recurring_invoicing_type == "pre-paid":
            return next_period_date_start + relativedelta(
                days=recurring_invoicing_offset
            )

        # post-paid
        return next_period_date_end + relativedelta(days=recurring_invoicing_offset)

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
        **kwargs,
    ):
        """Override to handle alignment logic."""
        align_billing_cycle = kwargs.get("align_billing_cycle")

        _logger.debug(
            "Alignment Check: start=%s, rule=%s, interval=%s, align=%s",
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            align_billing_cycle,
        )

        if align_billing_cycle and next_period_date_start:
            if next_period_date_start.day != 1:
                # Force end to be end of the current month
                next_period_date_end = next_period_date_start + relativedelta(day=31)

                if max_date_end and next_period_date_end > max_date_end:
                    next_period_date_end = max_date_end

                _logger.debug("Aligned period end to %s", next_period_date_end)
                return next_period_date_end

        # Base call. We must handle the fact that base doesn't have **kwargs.
        # We try to call with kwargs first (in case another module added them)
        try:
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
        except TypeError:
            return super().get_next_period_date_end(
                next_period_date_start,
                recurring_rule_type,
                recurring_interval,
                max_date_end,
                next_invoice_date=next_invoice_date,
                recurring_invoicing_type=recurring_invoicing_type,
                recurring_invoicing_offset=recurring_invoicing_offset,
            )
