# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    create_contract_at_sale_order_confirmation = fields.Boolean(
        string="Automatically Create Contracts At Sale Order Confirmation",
        default=True,
    )
