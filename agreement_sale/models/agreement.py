# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# © 2017 Akretion(Alexis de Lattre < alexis.delattre @ akretion.com >)

from odoo import fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    #sale_id = fields.Many2one('sale.order', string='Sales Order')
    sale_ids = fields.One2many(
        'sale.order', 'agreement_id', string='Sale Orders', readonly=True,
        domain=[('state', 'not in', ('draft', 'sent', 'cancel'))])
