# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict',
        readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='onchange')

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if invoice.agreement_id:
            values['agreement_id'] = invoice.agreement_id.id
        return values
