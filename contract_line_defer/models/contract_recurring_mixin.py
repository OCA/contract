# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractRecurringMixin(models.AbstractModel):
    _inherit = "contract.recurring.mixin"

    is_deferred = fields.Boolean(
        "Deferred", help="Do not invoice this line until it is activated"
    )

    def enable_deferred(self):
        self.ensure_one()
        self.is_deferred = True
