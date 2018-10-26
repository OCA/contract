# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.template'

    serviceprofile_ok = fields.Boolean(
        string='Include on Service Profile',
        default=False,
        help="Specify if the product can be selected in a service profile line"
    )
