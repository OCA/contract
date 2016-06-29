# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        invoice_obj = self.env['account.invoice']
        invoices = invoice_obj.browse(
            super(PurchaseOrderLine, self)._recurring_create_invoice(automatic))
        res = []
        unlink_list = []
        for partner in set(invoices.mapped('partner_id')):
            inv_to_merge = invoices.filtered(lambda x: x.partner_id == partner)
            if partner.contract_invoice_merge:
                invoices_merged = inv_to_merge.do_merge()
                res.extend(invoices_merged)
                unlink_list.extend(inv_to_merge)
            else:
                res.extend(inv_to_merge)
        for inv in unlink_list:
            inv.unlink()
        return res
