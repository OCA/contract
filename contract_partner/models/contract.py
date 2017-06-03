# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    service_partner_id = fields.Many2one(
        'res.partner',
        string="Service Location")

    contact_partner_id = fields.Many2one(
        'res.partner',
        string="Contact")

    @api.model
    def _prepare_invoice_data(self, contract):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice_data(contract)
        if contract.service_partner_id:
            invoice_vals['service_partner_id'] = contract.service_partner_id.id
        if contract.contact_partner_id:
            invoice_vals['contact_partner_id'] = contract.contact_partner_id.id
        return invoice_vals
