# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')],
    )

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        if self.partner_id.customer_payment_mode_id:
            self.payment_mode_id = self.partner_id.customer_payment_mode_id.id

    @api.model
    def _prepare_invoice_data(self, contract):
        invoice_vals = super(AccountAnalyticAccount, self)._prepare_invoice()
        if contract.payment_mode_id:
            invoice_vals['payment_mode_id'] = contract.payment_mode_id.id
            invoice_vals['partner_bank_id'] = (
                contract.partner_id.bank_ids[:1].id
            )
        return invoice_vals
