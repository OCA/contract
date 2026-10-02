# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContractTerminate(models.TransientModel):
    _inherit = "contract.contract.terminate"

    terminate_request_date = fields.Date(
        string="Termination Received On",
        required=True,
        default=fields.Date.context_today,
        help="Date on which the termination was received. It is used to check "
        "the termination notice.",
    )
    min_term_earliest_date = fields.Date(
        string="Earliest Termination Date",
        compute="_compute_min_term_earliest_date",
        help="Earliest possible termination date according to the minimum "
        "term and the termination notice.",
    )
    terminate_date = fields.Date(
        compute="_compute_terminate_date", store=True, readonly=False, precompute=True
    )
    is_terminated_before_min_term = fields.Boolean(
        string="Terminated Before Minimum Term",
        compute="_compute_is_terminated_before_min_term",
    )

    @api.depends("contract_id", "terminate_request_date")
    def _compute_min_term_earliest_date(self):
        for wizard in self:
            wizard.min_term_earliest_date = (
                wizard.contract_id
                and wizard.terminate_request_date
                and wizard.contract_id._get_min_term_contract_termination_date(
                    wizard.terminate_request_date
                )
            )

    @api.depends("min_term_earliest_date")
    def _compute_terminate_date(self):
        for wizard in self:
            wizard.terminate_date = (
                wizard.min_term_earliest_date
                or wizard.terminate_date
                or fields.Date.context_today(wizard)
            )

    @api.depends("terminate_date", "min_term_earliest_date")
    def _compute_is_terminated_before_min_term(self):
        for wizard in self:
            wizard.is_terminated_before_min_term = bool(
                wizard.terminate_date
                and wizard.min_term_earliest_date
                and wizard.terminate_date < wizard.min_term_earliest_date
            )

    def terminate_contract(self):
        for wizard in self:
            super(
                ContractContractTerminate,
                wizard.with_context(
                    min_term_request_date=wizard.terminate_request_date
                ),
            ).terminate_contract()
        return True
