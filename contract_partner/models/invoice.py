# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    service_partner_id = fields.Many2one(
        'res.partner',
        string="Service Address")

    contact_partner_id = fields.Many2one(
        'res.partner',
        string="Contact Address")
