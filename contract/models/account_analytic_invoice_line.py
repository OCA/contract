# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticInvoiceLine(models.Model):
    _name = 'account.analytic.invoice.line'
    _order = "sequence,id"

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        required=True,
        ondelete='cascade',
    )
    name = fields.Text(
        string='Description',
        required=True,
    )
    quantity = fields.Float(
        default=1.0,
        required=True,
    )
    uom_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        required=True,
    )
    price_unit = fields.Float(
        'Unit Price',
        required=True,
    )
    price_subtotal = fields.Float(
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'),
        string='Sub Total',
    )
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        help='Discount that is applied in generated invoices.'
             ' It should be less or equal to 100',
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Sequence of the contract line when displaying contracts",
    )
    date_from = fields.Date(
        string='Date From',
        compute='_compute_date_from',
        help='Date from invoiced period',
    )
    date_to = fields.Date(
        string='Date To',
        compute='_compute_date_to',
        help='Date to invoiced period',
    )

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

    def _compute_date_from(self):
        # When call from template line.analytic_account_id comodel is
        # 'account.analytic.contract',
        if self._name != 'account.analytic.invoice.line':
            return
        for line in self:
            contract = line.analytic_account_id
            date_start = (
                self.env.context.get('old_date') or fields.Date.from_string(
                    contract.recurring_next_date or fields.Date.today())
            )
            if contract.recurring_invoicing_type == 'pre-paid':
                date_from = date_start
            else:
                date_from = (date_start - contract.get_relative_delta(
                    contract.recurring_rule_type,
                    contract.recurring_interval) + relativedelta(days=1))
            line.date_from = fields.Date.to_string(date_from)

    def _compute_date_to(self):
        # When call from template line.analytic_account_id comodel is
        # 'account.analytic.contract',
        if self._name != 'account.analytic.invoice.line':
            return
        for line in self:
            contract = line.analytic_account_id
            date_start = (
                self.env.context.get('old_date') or fields.Date.from_string(
                    contract.recurring_next_date or fields.Date.today())
            )
            next_date = (
                self.env.context.get('next_date') or
                date_start + contract.get_relative_delta(
                    contract.recurring_rule_type, contract.recurring_interval)
            )
            if contract.recurring_invoicing_type == 'pre-paid':
                date_to = next_date - relativedelta(days=1)
            else:
                date_to = date_start
            line.date_to = fields.Date.to_string(date_to)

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

        if self.analytic_account_id._name == 'account.analytic.account':
            date = (
                self.analytic_account_id.recurring_next_date or
                fields.Datetime.now()
            )
            partner = self.analytic_account_id.partner_id

        else:
            date = fields.Datetime.now()
            partner = self.env.user.partner_id

        product = self.product_id.with_context(
            lang=partner.lang,
            partner=partner.id,
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
