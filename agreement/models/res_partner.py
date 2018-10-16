# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    agreements_ids = fields.One2many(
        'agreement',
        'name',
        string="Agreements"
    )
