# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def recurring_create_invoice(self):
        contracts = self.search(
            [('recurring_next_date', '<=', fields.Date.today()),
             ('account_type', '=', 'normal'),
             ('recurring_invoices', '=', True)]
        )
        res = super(AccountAnalyticAccount, self).recurring_create_invoice()
        if not contracts:
            return res
        invoices = self.env['account.invoice'].search([
            ('contract_id', 'in', contracts.ids)
        ])
        invoices2unlink = self.env['account.invoice']
        for partner in invoices.mapped('partner_id'):
            invoices2merge = invoices.filtered(
                lambda x: x.partner_id == partner)
            if partner.contract_invoice_merge and len(invoices2merge) > 1:
                invoices2merge.do_merge()
                invoices2unlink += invoices2merge
        invoices2unlink.unlink()
        return True
