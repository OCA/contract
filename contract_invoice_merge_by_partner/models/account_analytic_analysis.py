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
            super(PurchaseOrderLine, self)._recurring_create_invoice(automatic)
        )
        res = []
        unlink_list = []
        for partner in invoices.mapped('partner_id'):
            inv_to_merge = invoices.filtered(lambda x: x.partner_id == partner)
            if partner.contract_invoice_merge and (len(inv_to_merge) > 1):
                invoices_info = inv_to_merge.do_merge()
                res.extend(invoices_info.keys())
                for inv_ids_list in invoices_info.values():
                    unlink_list.extend(inv_ids_list)
            else:
                res.extend(inv_to_merge.ids)
        if unlink_list:
            invoice_obj.browse(unlink_list).unlink()
        return res
