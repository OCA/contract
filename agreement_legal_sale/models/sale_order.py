# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_template_id = fields.Many2one(
        'agreement',
        string="Agreement Template",
        domain="[('is_template', '=', True)]")

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            if order.agreement_template_id:
                order.agreement_id = order.agreement_template_id.copy(default={
                    'name': order.name,
                    'code': order.name,
                    'is_template': False,
                    'sale_id': order.id,
                    'partner_id': order.partner_id.id,
                    'analytic_account_id': order.analytic_account_id and
                    order.analytic_account_id.id or False,
                })
                for line in order.order_line:
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
