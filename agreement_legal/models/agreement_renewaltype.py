# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


# Main Agreement Section Records Model
class AgreementRenewalType(models.Model):
    _name = "agreement.renewaltype"
    _description = "Agreement Renewal Type"

    # General
    name = fields.Char(
        string="Title",
        required=True,
        help="Renewal types describe what happens after the "
        "agreement/contract expires.",
    )
    description = fields.Text(
        string="Description",
        required=True,
        help="Description of the renewal type."
    )
