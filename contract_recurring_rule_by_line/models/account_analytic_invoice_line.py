# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    recurring_next_date = fields.Date(
        default=fields.Date.context_today,
        copy=False,
        string='Date of Next Invoice',
    )
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic invoice generation.",
    )
    recurring_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
    )

    @api.multi
    def update_date(self):
        account_obj = self.env['account.analytic.account']
        for line in self:
            old_date = fields.Date.from_string(
                line.recurring_next_date)
            line.recurring_next_date = fields.Date.to_string(
                old_date +
                account_obj.get_relative_delta(
                    line.recurring_rule_type, line.recurring_interval))
