# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def prepare_contract_line_values(self, contract, quantity, max_sequence=0):
        self.ensure_one()
        return {
            "name": self.product_id.display_name or "/",
            "contract_id": contract.id,
            "product_id": self.product_id.id,
            "quantity": self.quantity * quantity,
            "uom_id": self.product_id.uom_id.id,
            "sequence": max_sequence + self.sequence,
            "discount": self.discount,
        }
