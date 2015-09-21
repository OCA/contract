# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _default_journal(self):
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=_default_journal,
        domain="[('type', '=', 'sale'),('company_id', '=', company_id)]")

    @api.model
    def _prepare_invoice_data(self, contract):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice_data(
            contract)
        if contract.journal_id:
            invoice_vals['journal_id'] = contract.journal_id.id
        return invoice_vals
