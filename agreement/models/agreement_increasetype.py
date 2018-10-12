from odoo import models, fields

#Main Agreement Increase Type Records Model
class AgreementIncreaseType(models.Model):
     _name = 'partner_agreement.increasetype'

#General
     name = fields.Char(string="Title", required=True, help="Increase types describe any increases that may happen during the contract.")
     description = fields.Text(string="Description", required=True, help="Description of the renewal type.")
     increase_percent = fields.Integer(string="Increase Percentage", help="Percentage that the amount will increase.")
