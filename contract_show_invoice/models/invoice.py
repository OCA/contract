# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.account_analytic_id')
    def _analytic_account_ids(self):
        self.analytic_account_ids = \
            self.mapped('invoice_line.account_analytic_id')

    analytic_account_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        compute='_analytic_account_ids',
        store=True,
        string='Contracts')
