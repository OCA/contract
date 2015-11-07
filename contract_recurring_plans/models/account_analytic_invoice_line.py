# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, invoice_id)
        if line.analytics_id:
            res.update({'account_analytic_id': False,
                        'analytics_id': line.analytics_id.id})
        return res


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = "account.analytic.invoice.line"

    analytics_id = fields.Many2one(
        comodel_name='account.analytic.plan.instance',
        string='Analytic Distribution')
