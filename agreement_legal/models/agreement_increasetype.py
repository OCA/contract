# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


# Main Agreement Increase Type Records Model
class AgreementIncreaseType(models.Model):
    _name = "agreement.increasetype"
    _description = "Agreement Increase Type"

    # General
    name = fields.Char(
        string="Title",
        required=True,
        help="Increase types describe any increases that may happen during "
        "the contract.",
    )
    description = fields.Text(
        string="Description",
        required=True,
        help="Description of the renewal type."
    )
    increase_percent = fields.Integer(
        string="Increase Percentage",
        help="Percentage that the amount will increase."
    )
