# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


# Main Agreement Section Records Model
class AgreementSubtype(models.Model):
    _name = 'agreement.subtype'

    # General
    name = fields.Char(
        string="Title",
        required=True
    )
    agreement_type_id = fields.Many2one(
        'agreement.type',
        string="Agreement Type"
    )
