# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError

from ..models.contract_line import EARLY_TERMINATION_GROUP


class ContractLineWizard(models.TransientModel):
    _inherit = "contract.line.wizard"

    min_term_request_date = fields.Date(
        string="Termination Received On",
        default=fields.Date.context_today,
        help="Date on which the termination was received. It is used to check "
        "the termination notice.",
    )
    min_term_earliest_date = fields.Date(
        string="Earliest Stop Date",
        compute="_compute_min_term_earliest_date",
        help="Earliest possible end date of the line according to the minimum "
        "term and the termination notice.",
    )
    is_stopped_before_min_term = fields.Boolean(
        string="Stopped Before Minimum Term",
        compute="_compute_is_stopped_before_min_term",
    )

    @api.depends("contract_line_id", "date_start", "min_term_request_date")
    def _compute_min_term_earliest_date(self):
        """Earliest end date of the line, or of its successor.

        Stopping a line keeps its own start date; a successor (only the
        successor wizards set ``date_start``) runs a new minimum term from its
        start date on.
        """
        for wizard in self:
            line = wizard.contract_line_id
            date_start = wizard.date_start or line.date_start
            wizard.min_term_earliest_date = (
                line
                and date_start
                and wizard.min_term_request_date
                and line._get_min_term_earliest_termination_date(
                    date_start, wizard.min_term_request_date
                )
            )

    @api.depends("date_end", "min_term_earliest_date")
    def _compute_is_stopped_before_min_term(self):
        for wizard in self:
            wizard.is_stopped_before_min_term = bool(
                wizard.date_end
                and wizard.min_term_earliest_date
                and wizard.date_end < wizard.min_term_earliest_date
            )

    @api.onchange("date_start", "min_term_request_date")
    def _onchange_min_term_request_date(self):
        # A later request may push the earliest date into the next term
        if self.min_term_earliest_date:
            self.date_end = self.min_term_earliest_date

    def stop(self):
        for wizard in self:
            super(
                ContractLineWizard,
                wizard.with_context(min_term_request_date=wizard.min_term_request_date),
            ).stop()
        return True

    def _check_min_term_successor(self):
        """Refuse a successor ending before its minimum term.

        Checked here and not in ``contract.line.plan_successor()``: renewals
        and suspensions plan successors on their own and must not be blocked.
        """
        self.ensure_one()
        if not self.is_stopped_before_min_term:
            return True
        line = self.contract_line_id
        if not self.env.user.has_group(EARLY_TERMINATION_GROUP):
            raise UserError(
                self.env._(
                    "The successor of %(line)s cannot end before %(date)s "
                    "(minimum term and termination notice).",
                    line=line.name,
                    date=self.min_term_earliest_date,
                )
            )
        line.contract_id.message_post(
            body=Markup(
                self.env._(
                    "Successor of contract line <strong>%(line)s</strong> ends "
                    "on %(date)s, before the end of the minimum term / "
                    "termination notice (%(earliest)s)."
                )
            )
            % {
                "line": line.name,
                "date": self.date_end,
                "earliest": self.min_term_earliest_date,
            }
        )
        return True

    def plan_successor(self):
        for wizard in self:
            wizard._check_min_term_successor()
        return super().plan_successor()
