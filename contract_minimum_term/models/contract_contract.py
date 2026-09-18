# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    min_term_date_end = fields.Date(
        string="Minimum Term End",
        compute="_compute_min_term_dates",
        store=True,
        help="Last day of the currently running minimum term (the latest one "
        "of all contract lines).",
    )
    min_term_notice_date = fields.Date(
        string="Termination Notice Deadline",
        compute="_compute_min_term_dates",
        store=True,
        help="Termination notice deadline of the contract line with the "
        "latest minimum term end.",
    )
    terminate_request_date = fields.Date(
        string="Termination Received On",
        readonly=True,
        copy=False,
        tracking=True,
    )
    is_terminated_before_min_term = fields.Boolean(
        string="Terminated Before Minimum Term",
        readonly=True,
        copy=False,
        tracking=True,
    )

    @api.depends(
        "contract_line_ids.min_term_date_end",
        "contract_line_ids.min_term_notice_date",
        "contract_line_ids.is_canceled",
    )
    def _compute_min_term_dates(self):
        for rec in self:
            lines = rec._get_min_term_lines().filtered("min_term_date_end")
            last_line = lines.sorted("min_term_date_end")[-1:]
            rec.min_term_date_end = last_line.min_term_date_end
            rec.min_term_notice_date = last_line.min_term_notice_date

    def _get_min_term_lines(self):
        self.ensure_one()
        return self.contract_line_ids.filtered(
            lambda line: not line.display_type and not line.is_canceled
        )

    def _get_min_term_contract_termination_date(self, request_date):
        """Earliest termination date of the whole contract: the latest one of
        all the lines, as the lines hold the minimum term configuration (either
        synchronized from the contract or set at line level).
        """
        self.ensure_one()
        dates = [
            line._get_min_term_earliest_termination_date(line.date_start, request_date)
            for line in self._get_min_term_lines()
        ]
        dates = [date for date in dates if date]
        return max(dates) if dates else False

    def action_cancel_contract_termination(self):
        res = super().action_cancel_contract_termination()
        self.write(
            {"terminate_request_date": False, "is_terminated_before_min_term": False}
        )
        return res

    def _terminate_contract(
        self,
        terminate_reason_id,
        terminate_comment,
        terminate_date,
        terminate_lines_with_last_date_invoiced=False,
    ):
        self.ensure_one()
        request_date = self.env.context.get(
            "min_term_request_date"
        ) or fields.Date.context_today(self)
        request_date = fields.Date.to_date(request_date)
        earliest_date = self._get_min_term_contract_termination_date(request_date)
        before_min_term = bool(earliest_date and terminate_date < earliest_date)
        if before_min_term and not self.env.user.has_group(
            "contract_minimum_term.group_early_termination"
        ):
            raise UserError(
                self.env._(
                    "The contract %(contract)s cannot be terminated before "
                    "%(date)s (minimum term and termination notice).",
                    contract=self.display_name,
                    date=earliest_date,
                )
            )
        res = super()._terminate_contract(
            terminate_reason_id,
            terminate_comment,
            terminate_date,
            terminate_lines_with_last_date_invoiced=(
                terminate_lines_with_last_date_invoiced
            ),
        )
        self.write(
            {
                "terminate_request_date": request_date,
                "is_terminated_before_min_term": before_min_term,
            }
        )
        if before_min_term:
            self.message_post(
                body=Markup(
                    self.env._(
                        "Contract terminated on %(date)s, before the end of the "
                        "minimum term / termination notice (%(earliest)s)."
                    )
                )
                % {"date": terminate_date, "earliest": earliest_date}
            )
        return res
