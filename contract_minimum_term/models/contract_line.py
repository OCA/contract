# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.contract_line_successor.models.contract_line_constraints import (
    get_allowed,
)

MINIMUM_TERM_DATE_FIELDS = ["min_term_date_end", "min_term_notice_date"]
EARLY_TERMINATION_GROUP = "contract_minimum_term.group_early_termination"


class ContractLine(models.Model):
    _inherit = "contract.line"

    min_term_date_end = fields.Date(
        string="Minimum Term End",
        compute="_compute_min_term_dates",
        store=True,
        copy=False,
        help="Last day of the currently running minimum term. The contract "
        "line cannot be terminated before this date.",
    )
    min_term_notice_date = fields.Date(
        string="Termination Notice Deadline",
        compute="_compute_min_term_dates",
        store=True,
        copy=False,
        help="A termination has to be received at the latest on this date, "
        "otherwise the minimum term is extended by the renewal term.",
    )

    @api.depends(
        "date_start",
        "min_term_interval",
        "min_term_rule_type",
        "is_auto_renew",
        "auto_renew_interval",
        "auto_renew_rule_type",
        "termination_notice_interval",
        "termination_notice_rule_type",
    )
    def _compute_min_term_dates(self):
        today = fields.Date.context_today(self)
        for rec in self:
            date_end = rec._get_min_term_date_end(rec.date_start, today)
            rec.min_term_date_end = date_end
            rec.min_term_notice_date = (
                date_end - rec._get_min_term_notice_delta() if date_end else False
            )

    def _get_min_term_earliest_termination_date(self, date_start, request_date):
        earliest = super()._get_min_term_earliest_termination_date(
            date_start, request_date
        )
        # A line which ends anyway is not restricted beyond its end date. A
        # successor starting after it has a term of its own.
        if earliest and self.date_end and self.date_end >= date_start:
            earliest = min(earliest, self.date_end)
        return earliest

    @api.constrains("is_auto_renew", "successor_contract_line_id", "date_end")
    def _check_allowed(self):
        """A line with a minimum term renews the term, not an end date.

        ``contract_line_successor`` requires an end date on an auto-renewing
        line. That check only applies to lines without a minimum term, the
        others stay open-ended on purpose.
        """
        min_term_lines = self.filtered(lambda rec: rec.min_term_interval > 0)
        res = super(ContractLine, self - min_term_lines)._check_allowed()
        for rec in min_term_lines:
            if rec.is_auto_renew and rec.successor_contract_line_id:
                raise ValidationError(
                    self.env._(
                        "A contract line with a successor can't be set to auto-renew"
                    )
                )
        return res

    @api.depends("min_term_interval")
    def _compute_allowed(self):
        """An open-ended line that renews its minimum term is allowed the same
        actions as any other open-ended line.

        ``get_allowed()`` has no entry for an auto renewing line without end
        date, because without a minimum term that combination cannot exist.
        """
        res = super()._compute_allowed()
        min_term_lines = self.filtered(
            lambda rec: rec.min_term_interval > 0
            and rec.is_auto_renew
            and not rec.date_end
            and not rec.contract_id.is_terminated
            and rec.date_start
        )
        for rec in min_term_lines:
            allowed = get_allowed(
                rec.date_start,
                rec.date_end,
                rec.last_date_invoiced,
                False,  # the renewal does not give the line an end date
                rec.successor_contract_line_id,
                rec.predecessor_contract_line_id,
                rec.is_canceled,
            )
            if allowed:
                rec.update(
                    {
                        "is_plan_successor_allowed": allowed.plan_successor,
                        "is_stop_plan_successor_allowed": allowed.stop_plan_successor,
                        "is_stop_allowed": allowed.stop,
                        "is_cancel_allowed": allowed.cancel,
                        "is_un_cancel_allowed": allowed.uncancel,
                    }
                )
        # A line under a minimum term that already started is stopped, not
        # taken back: cancelling it would remove the commitment silently.
        # cancel() still lets a user allowed to terminate early correct a line
        # that was never invoiced.
        if self.env.context.get("min_term_skip_checks"):
            return res
        for rec in self.filtered("is_cancel_allowed"):
            if rec.min_term_interval > 0 and rec._is_min_term_started():
                rec.is_cancel_allowed = False
        return res

    def _is_min_term_started(self):
        self.ensure_one()
        return bool(
            self.date_start and self.date_start <= fields.Date.context_today(self)
        )

    def _check_min_term_cancel(self):
        """Refuse cancelling a line that already started.

        A running line is stopped, not taken back. A user allowed to terminate
        before the minimum term may still cancel a line that was never
        invoiced, to correct a mistake.
        """
        self.ensure_one()
        if self.env.context.get("min_term_skip_checks"):
            return True
        if self.min_term_interval <= 0 or not self._is_min_term_started():
            return True
        if self.last_date_invoiced or not self.env.user.has_group(
            EARLY_TERMINATION_GROUP
        ):
            raise UserError(
                self.env._(
                    "The line %(line)s has started and has a minimum term: it "
                    "can be stopped, but not cancelled.",
                    line=self.name,
                )
            )
        return True

    def cancel(self):
        for rec in self:
            rec._check_min_term_cancel()
        # The check above replaces the one in _compute_allowed
        return super(
            ContractLine, self.with_context(min_term_skip_checks=True)
        ).cancel()

    def _get_min_term_request_date(self):
        return fields.Date.to_date(
            self.env.context.get("min_term_request_date")
        ) or fields.Date.context_today(self)

    def _check_min_term_stop(self, date_end):
        """Refuse stopping a line before the end of its minimum term.

        Same rule as the termination of the whole contract, so a line cannot
        be used to get around it.
        """
        self.ensure_one()
        if self.env.context.get("min_term_skip_checks"):
            return True
        request_date = self._get_min_term_request_date()
        earliest_date = self._get_min_term_earliest_termination_date(
            self.date_start, request_date
        )
        if not earliest_date or date_end >= earliest_date:
            return True
        if not self.env.user.has_group(EARLY_TERMINATION_GROUP):
            raise UserError(
                self.env._(
                    "The line %(line)s cannot be stopped before %(date)s "
                    "(minimum term and termination notice).",
                    line=self.name,
                    date=earliest_date,
                )
            )
        if not self.env.context.get("min_term_contract_termination"):
            # The termination of the whole contract logs it on its own
            self.contract_id.message_post(
                body=Markup(
                    self.env._(
                        "Contract line <strong>%(line)s</strong> stopped on "
                        "%(date)s, before the end of the minimum term / "
                        "termination notice (%(earliest)s)."
                    )
                )
                % {
                    "line": self.name,
                    "date": date_end,
                    "earliest": earliest_date,
                }
            )
        return True

    def action_stop(self):
        """Propose the earliest date the minimum term allows."""
        action = super().action_stop()
        earliest_date = self._get_min_term_earliest_termination_date(
            self.date_start, fields.Date.context_today(self)
        )
        if earliest_date:
            action["context"] = dict(action["context"], default_date_end=earliest_date)
        return action

    def stop(self, date_end, manual_renew_needed=False, post_message=True):
        for rec in self:
            rec._check_min_term_stop(date_end)
        return super().stop(
            date_end,
            manual_renew_needed=manual_renew_needed,
            post_message=post_message,
        )

    def _renew_minimum_term(self):
        """Recompute the minimum term of the given lines.

        The dates depend on the current date, so the recomputation has to be
        forced and propagated to the fields depending on them.
        """
        old_dates = {line: line.min_term_date_end for line in self}
        for field_name in MINIMUM_TERM_DATE_FIELDS:
            self.env.add_to_compute(self._fields[field_name], self)
        self._recompute_recordset(MINIMUM_TERM_DATE_FIELDS)
        self.modified(MINIMUM_TERM_DATE_FIELDS)
        for line in self:
            if line.min_term_date_end != old_dates[line]:
                line.contract_id.message_post(
                    body=Markup(
                        self.env._(
                            "Minimum term of <strong>%(line)s</strong> renewed "
                            "until %(date)s."
                        )
                    )
                    % {"line": line.name, "date": line.min_term_date_end}
                )
        return True

    @api.model
    def _get_min_term_renewal_domain(self):
        return [
            ("min_term_notice_date", "<", fields.Date.context_today(self)),
            ("is_auto_renew", "=", True),
            ("date_end", "=", False),
            ("is_canceled", "=", False),
            ("contract_id.is_terminated", "=", False),
        ]

    @api.model
    def _cron_renew_minimum_term(self):
        return self.search(self._get_min_term_renewal_domain())._renew_minimum_term()
