# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


SQL_SYNCHRONIZE1 = \
    """UPDATE account_analytic_invoice_line
 SET contract_id = analytic_account_id
 WHERE contract_id IS NULL"""

SQL_SYNCHRONIZE2 = \
    """UPDATE account_analytic_invoice_line
SET partner_id=subquery.partner_id,
    date_start=subquery.date_start,
    date_end=subquery.date_end
 FROM (SELECT
        l.id,
        c.partner_id,
        GREATEST(c.date_start, l.date_start) AS date_start,
        LEAST(c.date_end, l.date_end) AS date_end
      FROM account_analytic_invoice_line l
      JOIN account_analytic_account c
      ON l.contract_id = c.id
    WHERE (l.partner_id is NULL AND NOT c.partner_id IS NULL)
    OR (l.date_start is NULL AND NOT c.date_start IS NULL)
    OR (l.date_end is NULL AND NOT c.date_end IS NULL))
 AS subquery
 WHERE subquery.id = account_analytic_invoice_line.id"""


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    # We already had analytic_account_id to refer to the contract to which
    # this line belongs. Unfortunately this is overwritten by
    # account.analytic.contract.line which (ab)uses the same field to refer
    # to the contract template.
    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract',
        readonly=True,
        ondelete='cascade',
        index=True,
        store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True,
        store=True,
        related='contract_id.partner_id')
    # date_start and date_end are normally the same as on the contract.
    # However, making them not reference fields, but updating those if
    # needed when the contract changes allows to update a contract by changing
    # its lines.
    date_start = fields.Date(string='Line start date')
    date_end = fields.Date(string='Line end date')

    @api.multi
    def _limit_dates(self):
        """Keep line dates within contract dates."""
        for this in self:
            contract = this.contract_id
            line_vals = {}
            if contract.date_start:
                if (not this.date_start) or \
                        this.date_start < contract.date_start:
                    line_vals['date_start'] = contract.date_start
            if contract.date_end:
                if (not this.date_end) or \
                        this.date_end > contract.date_end:
                    line_vals['date_end'] = contract.date_end
            if line_vals:
                super(AccountAnalyticInvoiceLine, this).write(line_vals)

    @api.model
    def create(self, vals):
        """Make sure link between contract lines and contract is
        maintained and dates stay within limit of contract."""
        vals['contract_id'] = vals['analytic_account_id']
        result = super(AccountAnalyticInvoiceLine, self).create(vals)
        new_line._limit_dates()
        return result

    @api.multi
    def write(self, vals):
        """Keep line dates within contract dates on write."""
        result = super(AccountAnalyticInvoiceLine, self).write(vals)
        self._limit_dates()
        return result

    @api.model_cr
    def _register_hook(self):
        """Update existing contract lines to restore link with contract."""
        self.env.cr.execute(SQL_SYNCHRONIZE1)
        self.env.cr.execute(SQL_SYNCHRONIZE2)
