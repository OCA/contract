# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

MINIMUM_TERM_FIELDS = [
    "min_term_interval",
    "min_term_rule_type",
    "min_term_renewal_interval",
    "min_term_renewal_rule_type",
    "min_term_notice_interval",
    "min_term_notice_rule_type",
]

RULE_TYPES = [
    ("daily", "Day(s)"),
    ("weekly", "Week(s)"),
    ("monthly", "Month(s)"),
    ("yearly", "Year(s)"),
]


class ContractMinimumTermMixin(models.AbstractModel):
    _name = "contract.minimum.term.mixin"
    _description = "Contract Minimum Term Mixin"

    min_term_interval = fields.Integer(
        string="Minimum Term",
        help="Initial minimum term, counted from the start date. "
        "Leave 0 to disable the minimum term.",
    )
    min_term_rule_type = fields.Selection(
        RULE_TYPES,
        string="Minimum Term Type",
    )
    min_term_renewal_interval = fields.Integer(
        string="Renewal Term",
        help="If the contract is not terminated in time, the minimum term is "
        "extended by this term. Leave 0 to not extend the minimum term: once "
        "it is over, the contract can be terminated at any time respecting "
        "the termination notice.",
    )
    min_term_renewal_rule_type = fields.Selection(
        RULE_TYPES,
        string="Renewal Term Type",
    )
    min_term_notice_interval = fields.Integer(
        string="Termination Notice",
        help="The termination has to be received at least this long before "
        "the end of the minimum term (or before the termination date once "
        "the minimum term is over).",
    )
    min_term_notice_rule_type = fields.Selection(
        RULE_TYPES[:3],
        string="Termination Notice Type",
    )

    @api.model
    def _get_min_term_delta(self, rule_type, interval):
        return self.env["contract.recurring.mixin"].get_relative_delta(
            rule_type or "monthly", interval
        )

    def _get_min_term_notice_delta(self):
        self.ensure_one()
        if self.min_term_notice_interval <= 0:
            return relativedelta()
        return self._get_min_term_delta(
            self.min_term_notice_rule_type, self.min_term_notice_interval
        )

    def _get_min_term_date_end(self, date_start, reference_date):
        """Return the last day of the minimum term which is running at
        ``reference_date``.

        The initial minimum term is extended by the renewal term as long as
        the termination notice deadline of the current term is before
        ``reference_date``.
        """
        self.ensure_one()
        if not date_start or self.min_term_interval <= 0:
            return False
        one_day = relativedelta(days=1)
        initial_end = date_start + self._get_min_term_delta(
            self.min_term_rule_type, self.min_term_interval
        )
        if self.min_term_renewal_interval <= 0:
            return initial_end - one_day
        renewal_delta = self._get_min_term_delta(
            self.min_term_renewal_rule_type, self.min_term_renewal_interval
        )
        notice_delta = self._get_min_term_notice_delta()
        renewals = 0
        # Always derive the term end from the initial term end to avoid drift
        # on month ends (e.g. 28th of February)
        date_end = initial_end - one_day
        while reference_date > date_end - notice_delta:
            renewals += 1
            date_end = initial_end + renewal_delta * renewals - one_day
        return date_end

    def _get_min_term_earliest_termination_date(self, date_start, request_date):
        """Return the earliest allowed termination date for a termination
        received on ``request_date``, or False when there is no restriction.
        """
        self.ensure_one()
        if self.min_term_interval <= 0 and self.min_term_notice_interval <= 0:
            return False
        earliest = request_date + self._get_min_term_notice_delta()
        date_end = self._get_min_term_date_end(date_start, request_date)
        if date_end:
            earliest = max(earliest, date_end)
        return earliest
