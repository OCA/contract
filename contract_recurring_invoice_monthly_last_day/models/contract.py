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
import logging
import time


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    recurring_rule_type = fields.Selection(selection_add = [('monthlylastday', 'Month(s) - Last day')])

    def _recurring_create_invoice(self, cr, uid, ids, automatic=False, context=None):
        context = context or {}
        invoice_ids = []
        current_date =  time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search(cr, uid, [('recurring_next_date','<=', current_date), ('state','=', 'open'), ('recurring_invoices','=', True), ('type', '=', 'contract')])
        if contract_ids:
            cr.execute('SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s GROUP BY company_id', (tuple(contract_ids),))
            for company_id, ids in cr.fetchall():
                for contract in self.browse(cr, uid, ids, context=dict(context, company_id=company_id, force_company=company_id)):
                    try:
                        invoice_values = self._prepare_invoice(cr, uid, contract, context=context)
                        invoice_ids.append(self.pool['account.invoice'].create(cr, uid, invoice_values, context=context))
                        next_date = datetime.datetime.strptime(contract.recurring_next_date or current_date, "%Y-%m-%d")
                        interval = contract.recurring_interval
                        if contract.recurring_rule_type == 'daily':
                            new_date = next_date+relativedelta(days=+interval)
                        elif contract.recurring_rule_type == 'weekly':
                            new_date = next_date+relativedelta(weeks=+interval)
                        elif contract.recurring_rule_type == 'monthly':
                            new_date = next_date+relativedelta(months=+interval)
                        elif contract.recurring_rule_type == 'monthlylastday':
                            interval = interval + 1
                            new_date_plus1m = next_date+relativedelta(months=+interval)
                            new_date_plus1d = datetime.datetime(new_date_plus1m.year, new_date_plus1m.month, 1)
                            new_date = new_date_plus1d+relativedelta(days=-1)
                        else:
                            new_date = next_date+relativedelta(years=+interval)
                        self.write(cr, uid, [contract.id], {'recurring_next_date': new_date.strftime('%Y-%m-%d')}, context=context)
                        if automatic:
                            cr.commit()
                    except Exception:
                        if automatic:
                            cr.rollback()
                            _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
                        else:
                            raise
        return invoice_ids
