# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import api, fields, models

from .contract_minimum_term_mixin import MINIMUM_TERM_FIELDS


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

    @api.depends("date_start", *MINIMUM_TERM_FIELDS)
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
        # A line which ends anyway is not restricted beyond its end date
        if earliest and self.date_end:
            earliest = min(earliest, self.date_end)
        return earliest

    @api.model
    def _get_min_term_renewal_domain(self):
        return [
            ("min_term_notice_date", "<", fields.Date.context_today(self)),
            ("min_term_renewal_interval", ">", 0),
            ("is_canceled", "=", False),
            ("contract_id.is_terminated", "=", False),
        ]

    @api.model
    def cron_renew_minimum_term(self):
        lines = self.search(self._get_min_term_renewal_domain())
        old_dates = {line: line.min_term_date_end for line in lines}
        # The dates depend on the current date: force their recomputation and
        # propagate the new values to the dependent fields (contract dates)
        fnames = ["min_term_date_end", "min_term_notice_date"]
        for field_name in fnames:
            self.env.add_to_compute(self._fields[field_name], lines)
        lines._recompute_recordset(fnames)
        lines.modified(fnames)
        for line in lines:
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
