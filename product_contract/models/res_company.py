# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    create_contract_at_sale_order_confirmation = fields.Boolean(
        string="Automatically Create Contracts At Sale Order Confirmation",
        default=True,
    )
    constrain_contract_products = fields.Boolean(
        string="Enforce that all contract products have a contract template",
        default=False,
    )
