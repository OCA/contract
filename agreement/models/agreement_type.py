# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


# Main Agreement Section Records Model
class AgreementType(models.Model):
    _name = 'agreement.type'

    # General
    name = fields.Char(
        string="Title",
        required=True
    )
    agreement_subtypes_ids = fields.One2many(
        'agreement.subtype',
        'agreement_type_id',
        string="Agreement"
    )
