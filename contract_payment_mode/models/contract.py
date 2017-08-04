# -*- coding: utf-8 -*-
from odoo import api, fields, models


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

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(AccountAnalyticAccount, self)._prepare_invoice()
        if self.payment_mode_id:
            invoice_vals['payment_mode_id'] = self.payment_mode_id.id
            invoice = self.env['account.invoice'].new(invoice_vals)
            invoice.payment_mode_id_change()
            invoice_vals = invoice._convert_to_write(invoice._cache)
        return invoice_vals
