# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class Agreement(models.Model):
    _inherit = 'agreement'

    sale_ids = fields.One2many(
        'sale.order', 'agreement_id', string='Sale Orders', readonly=True,
        domain=[('state', 'not in', ('draft', 'sent', 'cancel'))])
