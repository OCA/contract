# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractManuallyCreateInvoice(models.TransientModel):
    _inherit = "contract.manually.create.invoice"

    def create_invoice_queued(self):
        return super(
            ContractManuallyCreateInvoice,
            self.with_context(invoice_date_forced=self.invoice_date_forced),
        ).create_invoice_queued()
