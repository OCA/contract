# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict',
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['agreement_id'] = self.agreement_id.id or False
        return vals
