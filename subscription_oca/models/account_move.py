# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Subscription"
    )

    def action_open_subscription(self):
        self.ensure_one()
        action = self.env.ref("subscription_oca.sale_subscription_action")
        action = action.read()[0]
        action["domain"] = [("id", "=", self.subscription_id.id)]
        return action
