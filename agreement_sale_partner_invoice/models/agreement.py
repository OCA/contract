# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields


class Agreement(models.Model):
    _inherit = 'agreement'

    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner', string='Invoiced Partner',
        help="Final partner to invoice according to ")
