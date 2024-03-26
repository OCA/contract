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
        sale_subscription.close_subscription(self.close_reason_id.id)
