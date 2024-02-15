# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticInvoiceLine(models.Model):
    _name = 'account.analytic.invoice.line'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(default=1.0, required=True)
    uom_id = fields.Many2one(
        'product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float('Unit Price', required=True)
    price_subtotal = fields.Float(
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'),
        string='Sub Total')
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        help='Discount that is applied in generated invoices.'
             ' It should be less or equal to 100')

    @api.multi
    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            if line.analytic_account_id.pricelist_id:
                cur = line.analytic_account_id.pricelist_id.currency_id
                line.price_subtotal = cur.round(subtotal)
            else:
                line.price_subtotal = subtotal

    @api.multi
    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(
                    _("Discount should be less or equal to 100"))

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

        date = (
            self.analytic_account_id.recurring_next_date or
            fields.Datetime.now()
        )

        product = self.product_id.with_context(
            lang=self.analytic_account_id.partner_id.lang,
            partner=self.analytic_account_id.partner_id.id,
            quantity=self.quantity,
            date=date,
            pricelist=self.analytic_account_id.pricelist_id.id,
            uom=self.uom_id.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        vals['price_unit'] = product.price
        self.update(vals)
        return {'domain': domain}
