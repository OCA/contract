# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _check_recurring_next_date_recurring_invoices(self):
        return super(
            ContractLine, self.filtered(lambda line: not line.is_deferred)
        )._check_recurring_next_date_recurring_invoices()
