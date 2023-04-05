# Copyright 2023 Manuel Calero (<https://xtendoo.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    client_order_ref = fields.Char(
        string="Customer Reference",
    )

    def _prepare_sale(self, date_ref):
        values = super()._prepare_sale(date_ref)
        if self.client_order_ref:
            values["client_order_ref"] = self.client_order_ref
        return values
