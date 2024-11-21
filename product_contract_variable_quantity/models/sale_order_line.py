# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_contract_line_values(self, contract, predecessor_contract_line=False):
        values = super()._prepare_contract_line_values(
            contract, predecessor_contract_line
        )
        values["qty_type"] = self.qty_type
        values["qty_formula_id"] = self.qty_formula_id.id
        return values
