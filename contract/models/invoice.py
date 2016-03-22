# -*- coding: utf-8 -*-
# © 2016 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Contract')
    analytic_account_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        compute='_compute_analytic_account_ids',
        store=True,
        string='Contracts')

    @api.multi
    @api.depends('invoice_line_ids.account_analytic_id')
    def _compute_analytic_account_ids(self):
        for invoice in self:
            invoice.analytic_account_ids = invoice.mapped(
                'invoice_line_ids.account_analytic_id'
            )
