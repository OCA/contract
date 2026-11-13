# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _inherit = ["sale.subscription", "portal.mixin"]

    def _compute_access_url(self):
        for subscription in self:
            subscription.access_url = f"/my/subscriptions/{subscription.id}"

    def action_preview(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": self.get_portal_url(),
        }
