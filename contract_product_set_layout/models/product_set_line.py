# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def prepare_contract_line_values(self, contract, quantity, max_sequence=0):
        res = super().prepare_contract_line_values(
            contract, quantity, max_sequence=max_sequence
        )
        res.update(
            {
                "display_type": self.display_type,
                "name": res.get("name") if not self.display_type else self.name,
            }
        )
        return res
