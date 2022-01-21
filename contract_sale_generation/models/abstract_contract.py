# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractAbstractContract(models.AbstractModel):
    _inherit = "contract.abstract.contract"

    sale_autoconfirm = fields.Boolean(string="Sale Autoconfirm")

    @api.model
    def _selection_generation_type(self):
        res = super()._selection_generation_type()
        res.append(("sale", "Sale"))
        return res
