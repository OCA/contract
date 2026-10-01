# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractManuallyCreateInvoice(models.TransientModel):
    _inherit = "contract.manually.create.invoice"

    invoice_date_forced = fields.Date(
        "Date to set on Invoice",
        help="If specified, this date will be set on the generated invoices instead of "
        "the contract's recurring date.",
    )

    def _create_invoices(self):
        invoices = super()._create_invoices()
        if self.invoice_date_forced:
            invoices.write({"invoice_date": self.invoice_date_forced})
        return invoices
