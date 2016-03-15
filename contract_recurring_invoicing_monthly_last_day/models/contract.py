# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2016 Binovo IT Human Project SL <elacunza@binovo.es>
#       Add monthlylastday support
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime
import time


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    recurring_rule_type = fields.Selection(selection_add = [('monthlylastday', 'Month(s) - Last day')])

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        domain_other = [('recurring_rule_type', '!=', 'monthlylastday')]
        recs_other = self.search(domain_other)
        invoice_ids = super(AccountAnalyticAccount, recs_other)._recurring_create_invoice(automatic)
        domain = [('recurring_rule_type', '=', 'monthlylastday')]
        recs_monthly_last_day = self.search(domain)
        if recs_monthly_last_day:
            current_date =  time.strftime('%Y-%m-%d')
            for contract in recs_monthly_last_day:
                try:
                     invoice_values = self._prepare_invoice(contract)
                     invoice_ids.append(self.env['account.invoice'].create(invoice_values))
                     next_date = datetime.datetime.strptime(contract.recurring_next_date or current_date, "%Y-%m-%d")
                     interval = contract.recurring_interval + 1
                     new_date_plus1m = next_date+relativedelta(months=+interval)
                     new_date_plus1d = datetime.datetime(new_date_plus1m.year, new_date_plus1m.month, 1)
                     new_date = new_date_plus1d+relativedelta(days=-1)
                     contract.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
                except Exception:
                     if automatic:
                         _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
                     else:
                         raise
        return invoice_ids