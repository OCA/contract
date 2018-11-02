# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_contract = fields.Boolean(
        string='Is a contract', related="product_id.is_contract"
    )
    contract_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Contract', copy=False
    )
    contract_template_id = fields.Many2one(
        comodel_name='account.analytic.contract',
        string='Contract Template',
        related='product_id.product_tmpl_id.contract_template_id',
        readonly=True
    )
    recurring_rule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('yearly', 'Year(s)'),
        ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic invoice generation.",
        copy=False,
    )
    recurring_invoicing_type = fields.Selection(
        [('pre-paid', 'Pre-paid'), ('post-paid', 'Post-paid')],
        default='pre-paid',
        string='Invoicing type',
        help="Specify if process date is 'from' or 'to' invoicing date",
        copy=False,
    )
    recurring_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
        copy=False,
    )
    date_start = fields.Date(string='Date Start', default=fields.Date.today())
    date_end = fields.Date(string='Date End', index=True)
    recurring_next_date = fields.Date(
        default=fields.Date.today(), copy=False, string='Date of Next Invoice'
    )

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id.is_contract:
            self.recurring_rule_type = self.product_id.recurring_rule_type
            self.recurring_invoicing_type = (
                self.product_id.recurring_invoicing_type
            )
            self.recurring_interval = self.product_id.recurring_interval

    @api.multi
    def _prepare_contract_line_values(self, contract):
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'product_id': self.product_id.id,
            'name': self.name,
            'quantity': self.product_uom_qty,
            'uom_id': self.product_uom.id,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'recurring_next_date': self.recurring_next_date
            or fields.Date.today(),
            'date_end': self.date_end,
            'date_start': self.date_start or fields.Date.today(),
            'recurring_interval': self.recurring_interval,
            'recurring_invoicing_type': self.recurring_invoicing_type,
            'recurring_rule_type': self.recurring_rule_type,
            'contract_id': contract.id,
            'sale_order_line_id': self.id,
        }

    @api.multi
    def create_contract_line(self, contract):
        contract_line = self.env['account.analytic.invoice.line']
        for rec in self:
            contract_line.create(rec._prepare_contract_line_values(contract))

    @api.constrains('contract_id')
    def _check_contract_sale_partner(self):
        for rec in self:
            if rec.contract_id:
                if rec.order_id.partner_id != rec.contract_id.partner_id:
                    raise ValidationError(
                        _(
                            "Sale Order and contract should be "
                            "linked to the same partner"
                        )
                    )

    @api.constrains('product_id', 'contract_id')
    def _check_contract_sale_contract_template(self):
        for rec in self:
            if rec.contract_id:
                if (
                    rec.contract_template_id
                    != rec.contract_id.contract_template_id
                ):
                    raise ValidationError(
                        _("Contract product has different contract template")
                    )
