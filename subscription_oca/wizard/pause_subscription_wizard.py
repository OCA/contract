# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PauseSubscriptionWizard(models.TransientModel):
    _name = "sale.subscription.pause.wizard"
    _description = "Pause subscription wizard"

    paused_until = fields.Date(
        string="Resume on",
        help="Optional date on which the subscription is automatically "
        "resumed by the cron. Leave empty to pause indefinitely.",
    )

    def button_confirm(self):
        subscription = self.env["sale.subscription"].browse(
            self.env.context["active_id"]
        )
        subscription.action_pause(paused_until=self.paused_until or None)
