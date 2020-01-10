# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id', 'contract_id')
    def _onchange_fsm_location_domain(self):
        domain = [('owner_id', 'child_of', self.partner_id.id)]
        if self.contract_id:
            domain = [('contract_ids', 'in', self.contract_id.id)]
        return {'domain': {'fsm_location_id': domain}}
