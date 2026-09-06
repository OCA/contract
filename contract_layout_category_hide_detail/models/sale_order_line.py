# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _hide_detail_contract_line_values(self):
        self.ensure_one()
        return {
            "show_details": self.show_details,
            "show_section_subtotal": self.show_section_subtotal,
            "show_subtotal": self.show_subtotal,
            "show_line_amount": self.show_line_amount,
        }

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        res = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id
        )
        res.update(self._hide_detail_contract_line_values())
        return res

    def _prepare_contract_line_section_values(self, contract):
        res = super()._prepare_contract_line_section_values(contract)
        res.update(self._hide_detail_contract_line_values())
        return res
