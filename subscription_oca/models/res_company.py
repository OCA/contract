# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    automatic_subscription_start = fields.Boolean(
        default=False,
        help="The subscription is automatically started when the sale order is"
        "confirmed. You may activate this feature if you don't want to review"
        "the subscription and you want to start the subscription at the order"
        "confirmation date",
    )
