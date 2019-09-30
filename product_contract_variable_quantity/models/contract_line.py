# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class ContractLine(models.Model):
    _inherit = 'contract.line'

    @api.onchange('product_id')
    def _onchange_product_id_recurring_info(self):
        res = super(ContractLine, self)._onchange_product_id_recurring_info()
        if self.product_id.is_contract:
            self.qty_type = self.product_id.qty_type
            self.qty_formula_id = self.product_id.qty_formula_id
        return res
