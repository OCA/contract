# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate',
        ondelete='restrict',
        string='Direct Debit Mandate',
        help="If mandate required in payment method and not set mandate, "
             "invoice takes the first valid mandate",
        index=True,
    )
    mandate_required = fields.Boolean(
        related='payment_mode_id.payment_method_id.mandate_required',
        readonly=True)
    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        readonly=True,
        string='Commercial Entity',
    )

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(AccountAnalyticAccount, self)._prepare_invoice()
        if self.mandate_id:
            invoice_vals['mandate_id'] = self.mandate_id.id
            invoice_vals['partner_bank_id'] = self.mandate_id.partner_bank_id.id
        elif self.payment_mode_id.payment_method_id.mandate_required:
            mandate = self.env['account.banking.mandate'].search([
                ('partner_id', '=', self.partner_id.commercial_partner_id.id),
                ('state', '=', 'valid'),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            invoice_vals['mandate_id'] = mandate.id
            invoice_vals['partner_bank_id'] = mandate.partner_bank_id.id
        return invoice_vals
