# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ContractManuallySingleInvoice(models.TransientModel):
    _inherit = "contract.manually.single.invoice"

    def create_invoice(self):
        if (
            self.contract_id.detect_exceptions()
            and not self.contract_id.ignore_exception
        ):
            action = self.contract_id._popup_exceptions()
            action.get("context").update({"default_date": self.date})
            return action
        return self.contract_id.generate_invoices_manually(date=self.date)
