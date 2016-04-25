# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    payment_mode_id = fields.Many2one(
        'payment.mode',
        string='Payment Mode',
        domain="[('sale_ok', '=', True)]")

    @api.multi
    def on_change_partner_id(self, partner_id, name):
        res = super(AccountAnalyticAccount, self).on_change_partner_id(
            partner_id,
            name)
        partner = self.env['res.partner'].browse(partner_id)
        if partner and partner.customer_payment_mode:
            res['value']['payment_mode_id'] = partner.customer_payment_mode.id
        return res

    @api.model
    def _prepare_invoice_data(self, contract):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice_data(contract)
        if contract.payment_mode_id:
            invoice_vals['payment_mode_id'] = contract.payment_mode_id.id
            invoice_vals['partner_bank_id'] = (
                contract.partner_id.bank_ids[:1].id or
                contract.payment_mode_id.bank_id.id)

        return invoice_vals
