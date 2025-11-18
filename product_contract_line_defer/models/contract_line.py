# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _onchange_product_id_recurring_info(self):
        res = super()._onchange_product_id_recurring_info()
        if self.product_id.is_contract and self.product_id.is_deferred:
            self.is_deferred = True
        return res
