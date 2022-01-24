# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    show_details = fields.Boolean(string="Show details", default=True)
    show_subtotal = fields.Boolean(string="Show subtotal", default=True)
    show_line_amount = fields.Boolean(string="Show line amount", default=True)

    def _prepare_invoice_line(self, move_form):
        """
        As contract module generate invoices, we fill in missing values
        here. (This should be done also on contract_sale_generation side)
        """
        res = super()._prepare_invoice_line(move_form=move_form)
        res.update(
            show_details=self.show_details,
            show_subtotal=self.show_subtotal,
            show_line_amount=self.show_line_amount,
        )
        return res
