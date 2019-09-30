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
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        help='Discount that is applied in generated invoices.'
        ' It should be less or equal to 100',
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    @api.multi
    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            if line.contract_id.pricelist_id:
                cur = line.contract_id.pricelist_id.currency_id
                line.price_subtotal = cur.round(subtotal)
            else:
                line.price_subtotal = subtotal
