# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractManuallySingleInvoice(models.TransientModel):
    _name = "contract.manually.single.invoice"
    _description = "Manually invoice a single contract"

    contract_id = fields.Many2one("contract.contract", required=True)
    date = fields.Date(required=True, default=lambda r: fields.Date.today())

    def create_invoice(self):
        return self.contract_id.generate_invoices_manually(date=self.date)
