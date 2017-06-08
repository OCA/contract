# -*- coding: utf-8 -*-
# Copyright 2015 Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _default_journal_id(self):
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=lambda s: s._default_journal_id(),
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
    )

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(AccountAnalyticAccount, self)._prepare_invoice()
        if self.journal_id:
            invoice_vals['journal_id'] = self.journal_id.id
        return invoice_vals
