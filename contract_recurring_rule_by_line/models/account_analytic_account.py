# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    recurring_next_date = fields.Date(
        string='Date of Next Invoice',
        compute='_compute_recurring_next_date'
    )

    @api.multi
    def update_date(self, old_date, new_date):
        self.ensure_one()
        recurring_lines = self.mapped('recurring_invoice_line_ids').filtered(
            lambda l: fields.Date.from_string(
                l.recurring_next_date) == old_date
        )
        recurring_lines.update_date()

    @api.multi
    @api.depends('recurring_invoice_line_ids.recurring_next_date')
    def _compute_recurring_next_date(self):
        for record in self:
            next_dates = record.recurring_invoice_line_ids.mapped(
                'recurring_next_date')
            record.recurring_next_date = next_dates and \
                min(next_dates) or fields.Date.today()

    @api.multi
    def _get_recurring_invoice_lines_to_invoice(self):
        lines = self.recurring_invoice_line_ids.filtered(
            lambda l: l.recurring_next_date ==
            l.analytic_account_id.recurring_next_date)
        return lines
