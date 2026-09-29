# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_invoice_line(self):
        res = super()._prepare_invoice_line()
        # An empty dict means an extension (e.g. contract_variable_quantity's
        # skip_zero_qty) nullified the line; don't resurrect it with our flags.
        if not res:
            return res
        res.update(
            show_details=self.show_details,
            show_subtotal=self.show_subtotal,
            show_section_subtotal=self.show_section_subtotal,
            show_line_amount=self.show_line_amount,
        )
        return res
