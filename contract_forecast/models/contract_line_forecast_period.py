# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ContractLineForecastPeriod(models.Model):

    _name = "contract.line.forecast.period"
    _description = "Contract Line Forecast Period"
    _order = "date_invoice, sequence"

    name = fields.Char(string="Name", required=True, readonly=True)
    sequence = fields.Integer(
        string="Sequence", related="contract_line_id.sequence", store=True
    )
    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=True,
        readonly=True,
        ondelete="cascade",
        related="contract_line_id.contract_id",
        store=True,
        index=True,
    )
    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line",
        required=True,
        readonly=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        readonly=True,
        related="contract_line_id.product_id",
        store=True,
        index=True,
    )
    date_start = fields.Date(string="Date Start", required=True, readonly=True)
    date_end = fields.Date(string="Date End", required=True, readonly=True)
    date_invoice = fields.Date(
        string="Invoice Date", required=True, readonly=True
    )
    quantity = fields.Float(default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(
        digits=dp.get_precision("Account"),
        string="Amount Untaxed",
        compute='_compute_price_subtotal',
        store=True
    )
    price_subtotal_signed = fields.Float(
        digits=dp.get_precision("Account"),
        string='Amount Untaxed Signed',
        compute='_compute_price_subtotal',
        store=True,
        help="Amount Untaxed, negative for purchase."
    )
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        help='Discount that is applied in generated invoices.'
        ' It should be less or equal to 100',
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    contract_type = fields.Selection(
        string='Contract Type',
        readonly=True,
        related="contract_id.contract_type",
        store=True,
        index=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        readonly=True,
        related="contract_line_id.contract_id.currency_id",
        store=True,
        index=True,
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Company Currency",
        related='company_id.currency_id',
        readonly=True
    )
    currency_rate = fields.Float(
        string='Currency Rate',
        readonly=True,
        group_operator="avg",
        compute='_compute_price_subtotal',
        groups="base.group_multi_currency",
        store=True
    )
    price_subtotal_company = fields.Monetary(
        string='Amount Untaxed in Company Currency',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_price_subtotal',
        help="Amount Untaxed in the currency of the company."
    )
    price_subtotal_company_signed = fields.Monetary(
        string='Amount Untaxed Signed in Company Currency',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_price_subtotal',
        help="Amount Untaxed Signed in the currency of the company, "
             "negative for purchase."
    )

    @api.multi
    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            sign = line.contract_type in ['purchase'] and -1 or 1
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            line.price_subtotal_signed = subtotal * sign
            line.price_subtotal_company_signed = line.price_subtotal_signed
            if (line.currency_id and line.company_id and
                    line.currency_id != line.company_id.currency_id):
                cur = line.currency_id
                line.price_subtotal = cur.round(subtotal)
                line.price_subtotal_signed = cur.round(line.price_subtotal_signed)
                rate_date = line.date_invoice or fields.Date.today()
                line.price_subtotal_company = cur._convert(
                    line.price_subtotal,
                    line.company_id.currency_id,
                    line.company_id, rate_date)
                line.price_subtotal_company_signed = line.price_subtotal_company * sign
                line.currency_rate = (line.price_subtotal_signed
                                      / line.price_subtotal_company_signed) or False
            else:
                line.price_subtotal = subtotal
                line.currency_rate = 1
