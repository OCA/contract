# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id', 'contract_id')
    def _onchange_fsm_location_domain(self):
        if self.contract_id:
            # Locations of the contract or the company (pickup at warehouse)
            domain = [
                '|',
                ('contract_ids', 'in', self.contract_id.id),
                ('owner_id', 'child_of', self.company_id.partner_id.id),
            ]
        else:
            # Locations of the customer or the company (pickup at warehouse)
            domain = [
                '|',
                ('owner_id', 'child_of', self.partner_id.id),
                ('owner_id', 'child_of', self.company_id.partner_id.id),
            ]
        return {'domain': {'fsm_location_id': domain}}
