# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.multi
    def _prepare_contract_value(self, contract_template):
        contract_values = super()._prepare_contract_value(contract_template)
        contract_values["transmit_method_id"] = self.transmit_method_id.id
        return contract_values
