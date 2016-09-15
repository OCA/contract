# -*- coding: utf-8 -*-
# Copyright 2016 Binovo IT Human Project SL
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')])

    @api.model
    def _prepare_invoice_data(self, contract):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice_data(contract)
        if contract.mandate_id:
            invoice_vals['mandate_id'] = contract.mandate_id.id
        return invoice_vals
