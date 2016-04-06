# -*- coding: utf-8 -*-
# © 2016 Binovo IT Human Project SL <elacunza@binovo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime
import logging
import time


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    recurring_rule_type = fields.Selection(
        selection_add=[('monthlylastday', 'Month(s) - Last day')])

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        invoice_ids = []
        current_date = time.strftime('%Y-%m-%d')
        if self.ids:
            contracts = self
        else:
            contracts = self.search(
                [('recurring_next_date','<=', current_date),
                 ('state','=', 'open'),
                 ('recurring_invoices','=', True),
                 ('type', '=', 'contract')])
        for contract in contracts:
            if contract.recurring_rule_type == 'monthlylastday':
                try:
                    invoice_values = self._prepare_invoice(contract)
                    invoice_ids.append(
                        self.env['account.invoice'].create(invoice_values))
                    next_date = datetime.datetime.strptime(
                        contract.recurring_next_date or current_date,
                        "%Y-%m-%d")
                    interval = contract.recurring_interval + 1
                    new_date_plus1m = next_date+relativedelta(months=+interval)
                    new_date_plus1d = datetime.datetime(new_date_plus1m.year,
                                                        new_date_plus1m.month,
                                                        1)
                    new_date = new_date_plus1d+relativedelta(days=-1)
                    contract.write(
                        {'recurring_next_date': new_date.strftime('%Y-%m-%d')})
                except Exception:
                    if automatic:
                        logging.exception(
                            'Fail to create recurring invoice for contract %s',
                            contract.code)
                    else:
                        raise
            else:
                invoice_ids.append(super(AccountAnalyticAccount, contract)
                                   ._recurring_create_invoice(automatic))
        return invoice_ids
