# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ContractManuallyCreateInvoice(models.TransientModel):
    _inherit = "contract.manually.create.invoice"

    def create_invoice_batch(self):
        self.ensure_one()

        for (
            records,
            description,
        ) in self.contract_to_invoice_ids._split_to_invoicing_chunks():
            description = f"Manual {description}"
            records.with_delay(description=description)._recurring_create_invoice()

        return {"type": "ir.actions.act_window_close"}
