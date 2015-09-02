# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.exceptions import ValidationError

from openerp.tools.translate import _

from openerp.osv import fields as old_fields


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = "account.analytic.invoice.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict,
                     context=None):
        res = super(AccountAnalyticInvoiceLine, self)._amount_line(
            cr, uid, ids, prop, unknow_none, unknow_dict, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            discount = (line.discount or 0) / 100
            res[line.id] = res[line.id] * (1 - discount)
        return res

    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        copy=True,
        help='Discount that is applied in generated invoices.'
        ' It should be less or equal to 100')

    _columns = {
        'price_subtotal': old_fields.function(
            _amount_line, string='Sub Total',
            type="float",
            digits_compute=dp.get_precision('Account')),
    }

    @api.one
    @api.constrains('discount')
    def _check_discount(self):
        if self.discount > 100:
            raise ValidationError(_("Discount should be less or equal to 100"))


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, fiscal_position):
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, fiscal_position)
        res['discount'] = line.discount or 0
        return res
