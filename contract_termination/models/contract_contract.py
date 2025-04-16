# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    is_terminated = fields.Boolean(string="Terminated", readonly=True, copy=False)
    terminate_reason_id = fields.Many2one(
        comodel_name="contract.terminate.reason",
        string="Termination Reason",
        ondelete="restrict",
        readonly=True,
        copy=False,
        tracking=True,
    )
    terminate_comment = fields.Text(
        string="Termination Comment",
        readonly=True,
        copy=False,
        tracking=True,
    )
    terminate_date = fields.Date(
        string="Termination Date",
        readonly=True,
        copy=False,
        tracking=True,
    )

    def action_terminate_contract(self):
        self.ensure_one()
        context = {"default_contract_id": self.id}
        return {
            "type": "ir.actions.act_window",
            "name": _("Terminate Contract"),
            "res_model": "contract.contract.terminate",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def action_cancel_contract_termination(self):
        self.ensure_one()
        self.write(
            {
                "is_terminated": False,
                "terminate_reason_id": False,
                "terminate_comment": False,
                "terminate_date": False,
            }
        )

    def _terminate_contract(
        self,
        terminate_reason_id,
        terminate_comment,
        terminate_date,
        terminate_lines_with_last_date_invoiced=False,
    ):
        self.ensure_one()
        if not self.env.user.has_group("contract_termination.can_terminate_contract"):
            raise UserError(_("You are not allowed to terminate contracts."))
        for line in self.contract_line_ids.filtered("is_stop_allowed"):
            line.stop(
                max(terminate_date, line.last_date_invoiced)
                if terminate_lines_with_last_date_invoiced and line.last_date_invoiced
                else terminate_date
            )
        self.write(
            {
                "is_terminated": True,
                "terminate_reason_id": terminate_reason_id.id,
                "terminate_comment": terminate_comment,
                "terminate_date": terminate_date,
            }
        )
        return True
