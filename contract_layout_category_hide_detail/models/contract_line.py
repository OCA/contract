# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_invoice_line(self, move_form):
        vals = super()._prepare_invoice_line(move_form)
        # If the line has skip_zero_qty field (provided by contract_variable
        # quantity module) set to 'True' and 'quantity' field' is zero then
        # 'vals' will be equal to {}
        if vals:
            vals.update(
                show_details=self.show_details, show_subtotal=self.show_subtotal,
            )
        return vals
