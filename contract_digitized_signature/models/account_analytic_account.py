# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):

    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'mail.thread']

    customer_signature = fields.Binary(
        string='Customer acceptance',
    )
    signature_name = fields.Char(
        string='Signed by',
    )

    @api.model
    def create(self, values):
        contract = super(AccountAnalyticAccount, self).create(values)
        if contract.customer_signature:
            values = {'customer_signature': contract.customer_signature}
            contract._track_signature(values, 'customer_signature')
        return contract

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(AccountAnalyticAccount, self).write(values)
