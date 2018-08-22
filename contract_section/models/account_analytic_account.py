# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        invoice_line_vals = super(AccountAnalyticAccount, self). \
            _prepare_invoice_line(line, invoice_id)
        invoice_line_vals.update({
            'layout_category_id': line.layout_category_id.id,
        })
        return invoice_line_vals
