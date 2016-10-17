# -*- coding: utf-8 -*-
# © 2016 Binovo IT Human Project SL <elacunza@binovo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime
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
                [('recurring_next_date', '<=', current_date),
                 ('state', '=', 'open'),
                 ('recurring_invoices', '=', True),
                 ('type', '=', 'contract')])
        for contract in contracts:
            is_monthlylastday = False
            orig_next_date = contract.recurring_next_date
            if contract.recurring_rule_type == 'monthlylastday':
                is_monthlylastday = True
                contract.recurring_rule_type = 'monthly'
            try:
                invoice_ids.append(super(AccountAnalyticAccount, contract)
                                   ._recurring_create_invoice(automatic))
            finally:
                if is_monthlylastday:
                    contract.recurring_rule_type = 'monthlylastday'
            # Note: recurring_next_day has been already incremented by super if
            # invoice was created. Adjust it to month's last day
            if is_monthlylastday \
                    and contract.recurring_next_date != orig_next_date:
                next_date = datetime.datetime.strptime(
                    contract.recurring_next_date,
                    "%Y-%m-%d")
                new_date = next_date + relativedelta(day=31)
                contract.write(
                    {'recurring_next_date': new_date.strftime('%Y-%m-%d')})
        return invoice_ids
