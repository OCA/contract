# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_agreement_id = fields.Many2one(
        'sale.agreement', string='Sale Agreement', ondelete='restrict',
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['sale_agreement_id'] = self.sale_agreement_id.id or False
        return vals
