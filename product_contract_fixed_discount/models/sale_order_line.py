from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        contract_line_data = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id=predecessor_contract_line_id
        )
        contract_line_data["discount_fixed"] = self.discount_fixed
        return contract_line_data
