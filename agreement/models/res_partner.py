from odoo import models, fields, api

class Partner(models.Model):

    _inherit = 'res.partner'

    agreements = fields.One2many('partner_agreement.agreement', 'name', string="Agreements")
