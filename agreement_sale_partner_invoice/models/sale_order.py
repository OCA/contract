# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_partner_invoice_id = fields.Many2one(
        comodel_name='res.partner', related='agreement_id.partner_invoice_id',
        string='Invoice Address', readonly=True,
        help="Invoice address for current sale order.")

    @api.model
    def create(self, vals):
        agreement_id = vals.get('agreement_id', False)
        if agreement_id:
            agreement = self.env['agreement'].browse(agreement_id)
            if agreement.partner_invoice_id:
                vals['partner_invoice_id'] = agreement.partner_invoice_id.id
        order = super(SaleOrder, self).create(vals)
        return order

    def write(self, vals):
        if 'agreement_id' in vals:
            agreement_id = vals.get('agreement_id')
            agreement = self.env['agreement'].browse(agreement_id)
            if agreement.partner_invoice_id:
                vals.update({'partner_invoice_id':
                             agreement.partner_invoice_id.id})
        return super(SaleOrder, self).write(vals)
