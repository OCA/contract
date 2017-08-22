# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class SaleAgreement(models.Model):
    _inherit = 'sale.agreement'

    sale_ids = fields.One2many(
        'sale.order', 'sale_agreement_id', string='Sale Orders', readonly=True,
        domain=[('state', 'not in', ('draft', 'sent', 'cancel'))])
