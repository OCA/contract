# Copyright 2025 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SubscriptionTemplate(models.Model):
    _inherit = "sale.subscription.template"

    invoicing_mode = fields.Selection(
        selection_add=[
            ("recurring_payment", "Invoice & Recurrent Payment"),
        ],
        ondelete={"recurring_payment": "set default"},
    )
