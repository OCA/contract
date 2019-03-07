# Copyright 2019 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        line_obj = self.env['account.invoice.line']
        invoice = self.env['account.invoice'].browse(
            invoice_id, prefetch=self._prefetch,
        )
        # Line with automatic price are not taken into account
        if (line.date_start and invoice.date_invoice < line.date_start) or \
                (line.date_end and invoice.date_invoice > line.date_end):
            return line_obj
        return super()._prepare_invoice_line(line, invoice_id)
