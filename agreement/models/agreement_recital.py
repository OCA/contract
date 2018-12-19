# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AgreementRecital(models.Model):
    _name = 'agreement.recital'
    _description = 'Agreement Recitals'
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    title = fields.Char(string="Title",
                        help="The title is displayed on the PDF."
                             "The name is not.")
    sequence = fields.Integer(string="Sequence", default=10)
    content = fields.Html(string="Content")
    agreement_id = fields.Many2one('agreement', string="Agreement",
                                   ondelete="cascade")
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide this recital without "
             "removing it.")
