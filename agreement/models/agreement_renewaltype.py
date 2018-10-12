from odoo import models, fields

#Main Agreement Section Records Model
class AgreementRenewalType(models.Model):
     _name = 'partner_agreement.renewaltype'

#General
     name = fields.Char(string="Title", required=True, help="Renewal types describe what happens after the agreement/contract expires.")
     description = fields.Text(string="Description", required=True, help="Description of the renewal type.")
