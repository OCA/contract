from odoo import models, fields

#Main Agreement Section Records Model
class AgreementType(models.Model):
     _name = 'partner_agreement.type'

#General
     name = fields.Char(string="Title", required=True)
     agreement_subtypes = fields.One2many('partner_agreement.subtype', 'agreement_type', string="Agreement")
