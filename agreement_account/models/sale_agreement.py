# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class SaleAgreement(models.Model):
    _name = 'sale.agreement'
    _description = 'Sale Agreement'

    code = fields.Char(
        string='Code', required=True, copy=False)
    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', ondelete='restrict', required=True,
        domain=[('customer', '=', True), ('parent_id', '=', False)])
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'sale.agreement'))
    active = fields.Boolean(string='Active', default=True)
    signature_date = fields.Date(string='Signature Date')
    invoice_ids = fields.One2many(
        'account.invoice', 'sale_agreement_id', string='Invoices',
        readonly=True)

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
        'This sale agreement code already exists for this customer!'
        )]
