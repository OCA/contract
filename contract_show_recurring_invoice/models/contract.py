# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_data(self, contract):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice_data(
            contract)
        invoice_vals['contract_id'] = contract.id
        return invoice_vals
