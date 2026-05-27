# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    subscription_id = fields.Many2one(
        comodel_name="sale.subscription",
        string="Subscription",
        index=True,
        ondelete="set null",
        help="Subscription this invoice line was generated from.",
    )
    subscription_period_start = fields.Date(
        string="Subscription period start",
        help="First day of the subscription period billed by this line.",
    )
    subscription_period_end = fields.Date(
        string="Subscription period end",
        help="Last day of the subscription period billed by this line.",
    )
