# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class Agreement(models.Model):
    _name = 'agreement'
    _description = 'Agreement'

    code = fields.Char(required=True, copy=False)
    name = fields.Char(required=True)
    agreement_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ], string='Type', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True,
        domain=[('parent_id', '=', False)])
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'agreement'))
    active = fields.Boolean(default=True)
    signature_date = fields.Date()
    out_invoice_ids = fields.One2many(
        'account.invoice', 'agreement_id', string='Customer Invoices',
        readonly=True, domain=[('type', 'in', ('out_invoice', 'out_refund'))])
    in_invoice_ids = fields.One2many(
        'account.invoice', 'agreement_id', string='Supplier Invoices',
        readonly=True, domain=[('type', 'in', ('in_invoice', 'in_refund'))])

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.code:
                name = u'[%s] %s' % (agr.code, agr.name)
            res.append((agr.id, name))
        return res

    _sql_constraints = [(
        'code_partner_company_unique',
        'unique(code, partner_id, company_id)',
        'This agreement code already exists for this partner!'
        )]
