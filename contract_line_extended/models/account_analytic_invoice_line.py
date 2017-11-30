# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV.
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
 FROM (SELECT l.id, c.partner_id, c.date_start, c.date_end
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
    date_start = fields.Date(
        string='Contract start date',
        readonly=True,
        store=True,
        related='contract_id.date_start')
    date_end = fields.Date(
        string='Contract end date',
        readonly=True,
        store=True,
        related='contract_id.date_end')

    @api.model
    def create(self, vals):
        """Make sure link between contract lines and contract is
        maintained."""
        vals['contract_id'] = vals['analytic_account_id']
        return super(AccountAnalyticInvoiceLine, self).create(vals)

    @api.model_cr
    def _register_hook(self):
        """Update existing contract lines to restore link with contract."""
        self.env.cr.execute(SQL_SYNCHRONIZE1)
        self.env.cr.execute(SQL_SYNCHRONIZE2)
