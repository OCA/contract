# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticContractLine(models.Model):

    _name = 'account.analytic.contract.line'
    _description = 'Contract Lines'
    _inherit = 'account.analytic.invoice.line'

    analytic_account_id = fields.Many2one(
        string='Contract',
        comodel_name='account.analytic.contract',
        required=True,
        ondelete='cascade',
    )

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'uom_id': []}}

        vals = {}
        domain = {'uom_id': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.uom_id or (self.product_id.uom_id.category_id.id !=
                               self.uom_id.category_id.id):
            vals['uom_id'] = self.product_id.uom_id

        product = self.product_id.with_context(
            lang=self.env.user.partner_id.lang,
            partner=self.env.user.partner_id.id,
            quantity=self.quantity,
            date=fields.Datetime.now(),
            pricelist=self.analytic_account_id.pricelist_id.id,
            uom=self.uom_id.id,
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        vals['price_unit'] = product.price
        self.update(vals)
        return {'domain': domain}
