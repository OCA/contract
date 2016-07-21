# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        invoice_ids = super(
            AccountAnalyticAccount, self)._recurring_create_invoice(automatic)
        invoices = self.env['account.invoice'].browse(invoice_ids)
        res = []
        invoices2unlink = self.env['account.invoice']
        for partner in invoices.mapped('partner_id'):
            invoices2merge = invoices.filtered(
                lambda x: x.partner_id == partner)
            if partner.contract_invoice_merge and len(invoices2merge) > 1:
                result = invoices2merge.do_merge()
                res += result.keys()
                invoices2unlink += invoices2merge
            else:
                res += invoices2merge.ids
        invoices2unlink.unlink()
        return res
