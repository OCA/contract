# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _prepare_sale(self, date_ref):
        """
        Fill in contract tag ids on sale order from contract values.
        """
        res = super()._prepare_sale(date_ref=date_ref)
        if self.tag_ids:
            res.update({"contract_tag_ids": [(6, 0, self.tag_ids.ids)]})
        return res
