# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            agreement_ids = self.env['agreement'].\
                search([('sale_id', '=', order.id)])
            agreement_ids.write({
                'fsm_location_id': order.partner_id.service_location_id})
        return res
