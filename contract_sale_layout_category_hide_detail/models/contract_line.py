from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_sale_line_vals(self, dates, order_id=False):
        sale_line_vals = super(ContractLine, self)._prepare_sale_line_vals(
            dates, order_id
        )
        sale_line_vals.update(
            {
                "show_details": self.show_details,
                "show_subtotal": self.show_subtotal,
                "show_section_subtotal": self.show_section_subtotal,
                "show_line_amount": self.show_line_amount,
            }
        )
        return sale_line_vals
