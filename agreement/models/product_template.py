# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.template'

    agreements_ids = fields.Many2many(
        'agreement',
        string="Agreements"
    )
