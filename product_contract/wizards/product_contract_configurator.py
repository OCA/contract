# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ProductContractConfigurator(models.TransientModel):
    _name = "product.contract.configurator"
    _inherit = "sale.order.line.contract.mixin"
    _description = "Product Contract Configurator Wizard"
