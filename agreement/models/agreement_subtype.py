from odoo import models, fields

#Main Agreement Section Records Model
class AgreementSubtype(models.Model):
     _name = 'partner_agreement.subtype'

#General
     name = fields.Char(string="Title", required=True)
     agreement_type = fields.Many2one('partner_agreement.type', string="Agreement Type")
