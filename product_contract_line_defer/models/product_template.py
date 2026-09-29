# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_deferred = fields.Boolean(
        "Defer Start by Default",
        help="Do not invoice this product until it is activated. Use this setting if "
        "you sell this product without knowing the contract start date at the "
        "conclusion of the sale.",
    )
