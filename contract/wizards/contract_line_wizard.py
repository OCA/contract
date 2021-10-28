# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractLineWizard(models.TransientModel):

    _name = "contract.line.wizard"
    _description = "Contract Line Wizard"

    date_start = fields.Date()
    date_end = fields.Date()
    recurring_next_date = fields.Date(string="Next Invoice Date")
    is_auto_renew = fields.Boolean(default=False)
    manual_renew_needed = fields.Boolean(
        default=False,
        help="This flag is used to make a difference between a definitive stop"
        "and temporary one for which a user is not able to plan a"
        "successor in advance",
    )
    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line",
        required=True,
        index=True,
        ondelete="cascade",
    )

    def stop(self):
        for wizard in self:
            wizard.contract_line_id.stop(
                wizard.date_end, manual_renew_needed=wizard.manual_renew_needed
            )
        return True

    def plan_successor(self):
        for wizard in self:
            wizard.contract_line_id.plan_successor(
                wizard.date_start, wizard.date_end, wizard.is_auto_renew
            )
        return True

    def stop_plan_successor(self):
        for wizard in self:
            wizard.contract_line_id.stop_plan_successor(
                wizard.date_start, wizard.date_end, wizard.is_auto_renew
            )
        return True

    def uncancel(self):
        for wizard in self:
            wizard.contract_line_id.uncancel(wizard.recurring_next_date)
        return True
