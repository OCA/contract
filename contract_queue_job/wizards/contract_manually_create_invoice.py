# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractManuallyCreateInvoice(models.TransientModel):
    _inherit = "contract.manually.create.invoice"

    def create_invoice(self):
        self.ensure_one()
        self.contract_to_invoice_ids._recurring_create_invoice()
        return {}
