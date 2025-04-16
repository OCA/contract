# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2016-2018 Tecnativa - Carlos Dauden
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractRecurringMixin(models.AbstractModel):
    """Abstract model to support recurring invoicing logic."""

    _name = "contract.recurring.mixin"
    _description = "Contract Recurring Mixin"

    date_start = fields.Date(
        index=True,
        default=lambda self: fields.Date.context_today(self),
        help="Contract activation date (first recurrence starts here)",
    )
    date_end = fields.Date(
        index=True, help="Optional contract termination date (limits recurrence)"
    )

    # === Recurrence Rule Fields ===
    # Define how often the contract recurs (e.g., monthly, yearly) and the interval.

    recurring_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Recurrence",
        help="Specify interval for automatic invoice generation.",
    )
    recurring_interval = fields.Integer(
        default=1,
        string="Invoice Every",
        help="Invoice every (Days/Week/Month/Year)",
    )
    recurring_invoicing_type = fields.Selection(
        [("pre-paid", "Pre-paid"), ("post-paid", "Post-paid")],
        default="pre-paid",
        string="Invoicing type",
        help=(
            "Specify if the invoice must be generated at the beginning "
            "(pre-paid) or end (post-paid) of the period."
        ),
    )
    recurring_invoicing_offset = fields.Integer(
        compute="_compute_recurring_invoicing_offset",
        string="Invoicing offset",
        help=(
            "Number of days to offset the invoice from the period end "
            "date (in post-paid mode) or start date (in pre-paid mode)."
        ),
    )
    # === Invoicing Configuration Fields ===
    # Define when and how invoices should be issued within the recurrence.

    last_date_invoiced = fields.Date(
        readonly=True,
        copy=False,
    )
    recurring_next_date = fields.Date(
        string="Date of Next Invoice",
        compute="_compute_recurring_next_date",
        store=True,
        readonly=False,
        copy=True,
    )
    next_period_date_start = fields.Date(
        string="Next Period Start",
        compute="_compute_next_period_date_start",
    )
    next_period_date_end = fields.Date(
        string="Next Period End",
        compute="_compute_next_period_date_end",
    )

    @api.depends("last_date_invoiced", "date_start", "date_end")
    def _compute_next_period_date_start(self):
        """Compute the start date of the next billing period."""
        for rec in self:
            if rec.last_date_invoiced:
                next_period_date_start = rec.last_date_invoiced + relativedelta(days=1)
            else:
                next_period_date_start = rec.date_start
            if (
                rec.date_end
                and next_period_date_start
                and next_period_date_start > rec.date_end
            ):
                next_period_date_start = False
            rec.next_period_date_start = next_period_date_start

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "recurring_next_date",
    )
    def _compute_next_period_date_end(self):
        """Compute the end date of the next billing period."""
        for rec in self:
            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_invoice_date=rec.recurring_next_date,
                recurring_invoicing_type=rec.recurring_invoicing_type,
                recurring_invoicing_offset=rec.recurring_invoicing_offset,
            )

    @api.depends("recurring_invoicing_type", "recurring_rule_type")
    def _compute_recurring_invoicing_offset(self):
        """Compute the invoicing offset based on type and rule."""
        for rec in self:
            method = self._get_default_recurring_invoicing_offset
            rec.recurring_invoicing_offset = method(
                rec.recurring_invoicing_type, rec.recurring_rule_type
            )

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
    )
    def _compute_recurring_next_date(self):
        """Compute the next invoice date."""
        for rec in self:
            rec.recurring_next_date = self.get_next_invoice_date(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
            )

    # === Utility Methods ===

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        """Return a relativedelta for one period based on rule type."""
        if recurring_rule_type == "daily":
            return relativedelta(days=interval)
        elif recurring_rule_type == "weekly":
            return relativedelta(weeks=interval)
        elif recurring_rule_type == "monthly":
            return relativedelta(months=interval)
        elif recurring_rule_type == "monthlylastday":
            return relativedelta(months=interval, day=1)
        elif recurring_rule_type == "quarterly":
            return relativedelta(months=3 * interval)
        elif recurring_rule_type == "semesterly":
            return relativedelta(months=6 * interval)
        else:  # yearly
            return relativedelta(years=interval)

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
    ):
        """Compute the end date for the next period."""
        if not next_period_date_start or (
            max_date_end and next_period_date_start > max_date_end
        ):
            return False

        if not next_invoice_date:
            # Regular case: use relative delta
            next_period_date_end = (
                next_period_date_start
                + self.get_relative_delta(recurring_rule_type, recurring_interval)
                - relativedelta(days=1)
            )
        else:
            # Forced invoice date: back-calculate period end
            if recurring_invoicing_type == "pre-paid":
                next_period_date_end = (
                    next_invoice_date
                    - relativedelta(days=recurring_invoicing_offset)
                    + self.get_relative_delta(recurring_rule_type, recurring_interval)
                    - relativedelta(days=1)
                )
            else:  # post-paid
                next_period_date_end = next_invoice_date - relativedelta(
                    days=recurring_invoicing_offset
                )

        if max_date_end and next_period_date_end > max_date_end:
            next_period_date_end = max_date_end
        return next_period_date_end

    @api.model
    def get_next_invoice_date(
        self,
        next_period_date_start,
        recurring_invoicing_type,
        recurring_invoicing_offset,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
    ):
        """Compute the date of the next invoice based on all parameters."""
        next_period_date_end = self.get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end=max_date_end,
        )
        if not next_period_date_end:
            return False

        if recurring_invoicing_type == "pre-paid":
            return next_period_date_start + relativedelta(
                days=recurring_invoicing_offset
            )
        else:
            return next_period_date_end + relativedelta(days=recurring_invoicing_offset)

    @api.model
    def _get_default_recurring_invoicing_offset(
        self, recurring_invoicing_type, recurring_rule_type
    ):
        """Return default offset in days based on invoicing type and rule."""
        if (
            recurring_invoicing_type == "pre-paid"
            or recurring_rule_type == "monthlylastday"
        ):
            return 0
        return 1
