# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    website_template_id = fields.Many2one(
        string='Website Template',
        comodel_name='account.analytic.contract.template',
        help='Website layout for contract',
    )
    account_invoice_ids = fields.Many2many(
        string='Invoices',
        comodel_name='account.invoice',
    )

    @api.model
    def _search_contracts(self, domain=None):
        partner = self.env.user.partner_id
        contract_mod = self.env['account.analytic.account']
        if not domain:
            domain = [
                ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
                ('recurring_invoices', '=', True),
            ]
        return contract_mod.search(domain)
