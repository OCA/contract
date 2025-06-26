# Copyright 2024 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models


class ProductContractConfigurator(models.TransientModel):
    _name = "product.contract.configurator"
    _inherit = "sale.order.line.contract.mixin"
    _description = "Product Contract Configurator Wizard"
