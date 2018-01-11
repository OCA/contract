# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _create_invoice(self):
        """Fully override super method to only take into account current
        lines.

        FIXME: The whole invoice creation should really look at periods
        already invoiced and periods still to be invoiced, combined with
        pre or post payment. This would also allow partial invoicing if
        an end or start date makes the contract period not a multiple
        of the invoicing period. For instance a yearly contract is
        cancelled during the year.
        """
        self.ensure_one()
        invoice_vals = self._prepare_invoice()
        invoice = self.env['account.invoice'].create(invoice_vals)
        for line in self.recurring_invoice_line_ids:
            if line.date_start <= self.recurring_next_date and \
                    line.date_end >= self.recurring_next_date:
                invoice_line_vals = self._prepare_invoice_line(
                    line, invoice.id)
                self.env['account.invoice.line'].create(invoice_line_vals)
        invoice.compute_taxes()
        return invoice

    @api.multi
    def _update_lines(self):
        """Keep lines within date limits of contract."""
        for this in self:
            for line in this.recurring_invoice_line_ids:
                line._limit_dates()

    @api.model
    def create(self, vals):
        result = super(AccountAnalyticAccount, self).create(vals)
        if 'recurring_invoice_line_ids' in vals:
            result._update_lines()
        return result

    @api.multi
    def write(self, vals):
        result = super(AccountAnalyticAccount, self).write(vals)
        # keep line date_start and date_end within contract limits:
        if 'date_start' in vals or 'date_end' in vals or \
                'recurring_invoice_line_ids' in vals:
            self._update_lines()
        return result
