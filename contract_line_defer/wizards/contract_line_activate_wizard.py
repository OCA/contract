# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractLineActivateWizard(models.TransientModel):
    _name = "contract.line.activate.wizard"
    _description = "Contract Line Activate Wizard"

    contract_line_id = fields.Many2one(
        "contract.line", required=True, ondelete="cascade"
    )
    date_start = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help="Contract activation date (first recurrence starts here)",
    )
    date_end = fields.Date(
        help="Optional contract termination date (limits recurrence)"
    )

    def activate_line(self):
        self.ensure_one()
        self.contract_line_id.is_deferred = False
        self.contract_line_id.date_start = self.date_start
        self.contract_line_id.date_end = self.date_end
