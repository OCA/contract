# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_contract = fields.Boolean(
        string='Is a contract', related="product_id.is_contract"
    )
    contract_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Contract'
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
