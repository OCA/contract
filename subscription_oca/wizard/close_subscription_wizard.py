# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CloseSubscriptionWizard(models.TransientModel):
    _name = "close.reason.wizard"
    _description = "Close reason wizard"

    close_reason_id = fields.Many2one(
        comodel_name="sale.subscription.close.reason", string="Reason"
    )

    def button_confirm(self):
        sale_subscription = self.env["sale.subscription"].browse(
            self.env.context["active_id"]
        )
        sale_subscription.close_reason_id = self.close_reason_id.id
        stage = sale_subscription.stage_id
        closed_stage = self.env["sale.subscription.stage"].search(
            [("type", "=", "post")], limit=1
        )
        if stage != closed_stage:
            sale_subscription.stage_id = closed_stage
            sale_subscription.active = False
