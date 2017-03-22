# -*- coding: utf-8 -*-
# © 2015 Angel Moya <angel.moya@domatix.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

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
