# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractRecurrencyBasicMixin(models.AbstractModel):
    _name = "contract.recurrency.basic.mixin"
    _description = "Basic recurrency mixin for abstract contract models"

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
        help="Specify Interval for automatic invoice generation.",
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
    recurring_interval = fields.Integer(
        default=1, string="Invoice Every", help="Invoice every (Days/Week/Month/Year)",
    )
    date_start = fields.Date(string="Date Start")
    recurring_next_date = fields.Date(string="Date of Next Invoice")

    @api.depends("recurring_invoicing_type", "recurring_rule_type")
    def _compute_recurring_invoicing_offset(self):
        for rec in self:
            method = self._get_default_recurring_invoicing_offset
            rec.recurring_invoicing_offset = method(
                rec.recurring_invoicing_type, rec.recurring_rule_type
            )

    @api.model
    def _get_default_recurring_invoicing_offset(
        self, recurring_invoicing_type, recurring_rule_type
    ):
        if (
            recurring_invoicing_type == "pre-paid"
            or recurring_rule_type == "monthlylastday"
        ):
            return 0
        else:
            return 1


class ContractRecurrencyMixin(models.AbstractModel):
    _inherit = "contract.recurrency.basic.mixin"
    _name = "contract.recurrency.mixin"
    _description = "Recurrency mixin for contract models"

    date_start = fields.Date(default=lambda self: fields.Date.context_today(self))
    recurring_next_date = fields.Date(
        compute="_compute_recurring_next_date", store=True, readonly=False, copy=True
    )
    date_end = fields.Date(string="Date End", index=True)
    next_period_date_start = fields.Date(
        string="Next Period Start", compute="_compute_next_period_date_start",
    )
    next_period_date_end = fields.Date(
        string="Next Period End", compute="_compute_next_period_date_end",
    )
    last_date_invoiced = fields.Date(
        string="Last Date Invoiced", readonly=True, copy=False
    )

    @api.depends("next_period_date_start")
    def _compute_recurring_next_date(self):
        self.recurring_next_date = False
        for rec in self.filtered("next_period_date_start"):
            rec.recurring_next_date = self.get_next_invoice_date(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
            )

    @api.depends("last_date_invoiced", "date_start", "date_end")
    def _compute_next_period_date_start(self):
        for rec in self:
            if rec.last_date_invoiced:
                next_period_date_start = rec.last_date_invoiced + relativedelta(days=1)
            else:
                next_period_date_start = rec.date_start
            if rec.date_end and next_period_date_start > rec.date_end:
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

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        """Return a relativedelta for one period.

        When added to the first day of the period,
        it gives the first day of the next period.
        """
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
        else:
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
        """Compute the end date for the next period.

        The next period normally depends on recurrence options only.
        It is however possible to provide it a next invoice date, in
        which case this method can adjust the next period based on that
        too. In that scenario it required the invoicing type and offset
        arguments.
        """
        if not next_period_date_start:
            return False
        if max_date_end and next_period_date_start > max_date_end:
            # start is past max date end: there is no next period
            return False
        if not next_invoice_date:
            # regular algorithm
            next_period_date_end = (
                next_period_date_start
                + self.get_relative_delta(recurring_rule_type, recurring_interval)
                - relativedelta(days=1)
            )
        else:
            # special algorithm when the next invoice date is forced
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
            # end date is past max_date_end: trim it
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
        next_period_date_end = self.get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end=max_date_end,
        )
        if not next_period_date_end:
            return False
        if recurring_invoicing_type == "pre-paid":
            recurring_next_date = next_period_date_start + relativedelta(
                days=recurring_invoicing_offset
            )
        else:  # post-paid
            recurring_next_date = next_period_date_end + relativedelta(
                days=recurring_invoicing_offset
            )
        return recurring_next_date
