# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_auto_payment_subscriptions(self):
        # Invoices of the "Sale order & Invoice" mode are linked via the order
        return (
            self.subscription_id
            | self.line_ids.sale_line_ids.order_id.order_subscription_id
        ).filtered("auto_create_payment")
