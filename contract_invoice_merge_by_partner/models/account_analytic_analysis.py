# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _get_contracts2invoice(self, rest_contracts):
        """Invoice together contracts from partners that have the option
        checked and that have several contracts to invoice"""
        if self.partner_id.contract_invoice_merge:
            return rest_contracts.filtered(
                lambda x: x.partner_id == self.partner_id
            ) | self
        return super(AccountAnalyticAccount, self)._get_contracts2invoice(
            rest_contracts
        )
