from odoo import models, fields

#Main Agreement Status Records Model
class AgreementStatus(models.Model):
     _name = 'partner_agreement.type'

#General
     name = fields.Char(string="Title", required=True)
