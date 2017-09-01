# -*- coding: utf-8 -*-
# © 2015 Angel Moya <angel.moya@domatix.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection(selection_add=[
        ('purchase', _('Purchase'))
    ])

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()

        if self.type == 'purchase':
            journal = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

            res = super(
                AccountAnalyticAccount,
                self.with_context(
                    contract_journal=journal
                )
            )._prepare_invoice()

            res.update({
                'journal_id': journal.id,
                'type': 'in_invoice'
            })

            return res
        else:
            return super(AccountAnalyticAccount, self)._prepare_invoice()

        return res

    def fields_get(
            self, cr, user, allfields=None, context=None, write_access=True,
            attributes=None
    ):
        if not context:
            context = {}

        res = super(AccountAnalyticAccount, self).fields_get(
            cr, user, allfields, context, write_access, attributes)
        if all((
                'partner_id' in res,
                context.get('default_type') == 'contract_purchase'
        )):
            res['partner_id']['string'] = _("Vendor")
        return res

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'purchase':
            self.journal_id = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

        super(AccountAnalyticAccount, self)._onchange_type()
