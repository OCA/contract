# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_contract_count(self):
        for rec in self:
            super()._compute_contract_count()
            if rec.fsm_location:
                locations = self.env['fsm.location'].search([
                    ('partner_id', '=', rec.id),
                ])
                contracts = self.env['contract.contract'].search([
                    '|',
                    ('partner_id', '=', rec.id),
                    ('fsm_location_ids', 'in', locations.ids),
                ])
                rec.sale_contract_count = len(contracts)

    def act_show_contract(self):
        action = super().act_show_contract()
        for rec in self:
            if rec.fsm_location:
                locations = self.env['fsm.location'].search([
                    ('partner_id', '=', rec.id),
                ])
                contracts = self.env['contract.contract'].search([
                    '|',
                    ('partner_id', '=', rec.id),
                    ('fsm_location_ids', 'in', locations.ids),
                ])
                action['domain'] = [('id', 'in', contracts.ids)]
                action['context'].pop('search_default_partner_id')
                action['context'].pop('default_partner_id')
                action['context'].pop('default_pricelist_id')
        return action
