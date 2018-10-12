from odoo import models, fields, api

class Product(models.Model):

    _inherit = 'product.template'

    agreements = fields.Many2many('partner_agreement.agreement', string="Agreements")
