# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# © 2017 Akretion(Alexis de Lattre < alexis.delattre @ akretion.com >)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_template_id = fields.Many2one(
        'agreement',
        string="Agreement Template",
        domain="[('is_template', '=', True)]")
    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict',
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]}, copy=False)

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['agreement_id'] = self.agreement_id.id or False
        return vals

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            if order.agreement_template_id:
                order.agreement_id = order.agreement_template_id.copy(default={
                    'name': order.name,
                    'code': order.name,
                    'is_template': False,
                    'partner_id': order.partner_id.id,
                    'analytic_account_id':
                        order.analytic_account_id and
                        order.analytic_account_id.id or False,
                })
                for line in self.order_line:
                    # Create agreement line
                    self.env['agreement.line'].create({
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'agreement_id': order.agreement_id.id,
                        'qty': line.product_uom_qty,
                        'sale_line_id': line.id,
                        'uom_id': line.product_uom.id
                    })
                    # If the product is a service profile, create one
                    if line.product_id.product_tmpl_id.is_serviceprofile:
                        self.env['agreement.serviceprofile'].create({
                            'name': line.name,
                            'agreement_id': order.agreement_id.id,
                        })
        return res
