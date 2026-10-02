# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

MINIMUM_TERM_FIELDS = [
    "min_term_interval",
    "min_term_rule_type",
]

RULE_TYPES = [
    ("daily", "Day(s)"),
    ("weekly", "Week(s)"),
    ("monthly", "Month(s)"),
    ("yearly", "Year(s)"),
]


class ContractMinimumTermMixin(models.AbstractModel):
    """Minimum term of a contract (line).

    The renewal of the minimum term and the termination notice reuse the
    fields of ``contract_line_successor``: ``is_auto_renew`` together with
    ``auto_renew_interval`` / ``auto_renew_rule_type`` renews the minimum
    term instead of an end date, and ``termination_notice_interval`` /
    ``termination_notice_rule_type`` is the notice to respect.
    """

    _name = "contract.minimum.term.mixin"
    _description = "Contract Minimum Term Mixin"

    min_term_interval = fields.Integer(
        string="Minimum Term",
        help="Initial minimum term, counted from the start date. The contract "
        "cannot be terminated before the end of this term. Leave 0 to disable "
        "the minimum term.",
    )
    min_term_rule_type = fields.Selection(
        RULE_TYPES,
        string="Minimum Term Type",
    )

    @api.model
    def _get_min_term_delta(self, rule_type, interval):
        return self.env["contract.recurring.mixin"].get_relative_delta(
            rule_type or "monthly", interval
        )

    def _get_min_term_notice_delta(self):
        """Termination notice, from ``contract_line_successor``."""
        self.ensure_one()
        if self.termination_notice_interval <= 0:
            return relativedelta()
        return self._get_min_term_delta(
            self.termination_notice_rule_type, self.termination_notice_interval
        )

    def _get_min_term_renewal_delta(self):
        """Renewal term of the minimum term, from ``contract_line_successor``.

        An empty delta means that the minimum term is not renewed: once it is
        over, the contract can be terminated at any time, respecting the
        termination notice.
        """
        self.ensure_one()
        if not self.is_auto_renew or self.auto_renew_interval <= 0:
            return relativedelta()
        return self._get_min_term_delta(
            self.auto_renew_rule_type, self.auto_renew_interval
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
        renewal_delta = self._get_min_term_renewal_delta()
        if not renewal_delta:
            return initial_end - one_day
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
        received on ``request_date``, or False when there is no minimum term.
        """
        self.ensure_one()
        if self.min_term_interval <= 0:
            return False
        earliest = request_date + self._get_min_term_notice_delta()
        date_end = self._get_min_term_date_end(date_start, request_date)
        if date_end:
            earliest = max(earliest, date_end)
        return earliest
