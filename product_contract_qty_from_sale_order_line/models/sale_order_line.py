# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    def _get_contract_line_qty(self):
        """Returns the quantity to be put on new contract lines."""
        self.ensure_one()
        return self.product_uom_qty
