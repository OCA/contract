# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from dateutil.relativedelta import relativedelta


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    start_end_dates_option = fields.Selection([
        ('past', 'Past Period'),
        ('future', 'Future Period'),
        ], string='Start/End Dates Option', default='future')

    @api.model
    def _prepare_invoice_line(self, line, fiscal_position):
        '''This method is used only for recurring invoices'''
        vals = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, fiscal_position)
        freq = line.analytic_account_id.recurring_rule_type
        option = line.analytic_account_id.start_end_dates_option or 'future'
        freq2delta = {
            'daily': 'days',
            'weekly': 'weeks',
            'monthly': 'months',
            'yearly': 'years',
            }
        if freq:
            if freq not in freq2delta:
                raise UserError(_(
                    "Contract frequence '%s' is not supported by the "
                    "module contract_start_end_dates") % freq)
            today_dt = fields.Date.from_string(
                fields.Date.context_today(self))
            delta_args = {freq2delta[freq]: 1}
            if option == 'future':
                start_date_dt = today_dt
                end_date_dt = start_date_dt - relativedelta(days=1)
                end_date_dt += relativedelta(**delta_args)
            elif option == 'past':
                end_date_dt = today_dt
                start_date_dt = end_date_dt + relativedelta(days=1)
                start_date_dt -= relativedelta(**delta_args)
            vals.update({
                'start_date': start_date_dt,
                'end_date': end_date_dt,
                })
        return vals
