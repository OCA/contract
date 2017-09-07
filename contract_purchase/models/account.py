# -*- coding: utf-8 -*-
# © 2017 Stefan Becker <s.becker@humanilog.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection(selection_add=[
        ('purchase', _('Purchase'))
    ])

    @api.multi
    def _prepare_invoice(self):
        contract = self[:1]

        if contract.type == 'purchase':
            journal = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', contract.company_id.id)
            ], limit=1)

            res = super(
                AccountAnalyticAccount,
                self.with_context(
                    contract_journal=journal
                )
            )._prepare_invoice()

            res.update({
                'type': 'in_invoice'
            })

            return res
        else:
            return super(AccountAnalyticAccount, self)._prepare_invoice()

        return res

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'purchase':
            self.journal_id = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

        super(AccountAnalyticAccount, self)._onchange_type()
