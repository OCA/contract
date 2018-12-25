# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AgreementServiceProfile(models.Model):
    _name = 'agreement.serviceprofile'
    _description = 'Agreement Service Profiles'

    name = fields.Char(string="Name", required=True)
    agreement_id = fields.Many2one('agreement', string="Agreement",
                                   ondelete="cascade")
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide this service profile"
             " without removing it.")
