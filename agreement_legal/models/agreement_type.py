# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AgreementType(models.Model):
    _name = "agreement.type"
    _description = "Agreement Types"

    name = fields.Char(string="Name", required=True)
    agreement_subtypes_ids = fields.One2many(
        "agreement.subtype",
        "agreement_type_id",
        string="Subtypes"
    )
