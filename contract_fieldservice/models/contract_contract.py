# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    fsm_location_ids = fields.Many2many(
        'fsm.location', 'contract_fsm_location',
        'contract_id', 'fsm_location_id', string='Service Locations',
        compute='compute_fsm_locations', readonly=True, store=True, index=True)

    @api.model
    @api.depends('contract_line_ids.fsm_location_id')
    def compute_fsm_locations(self):
        for rec in self:
            location_ids = []
            for line in rec.contract_line_ids:
                location_ids.append(
                    line.fsm_location_id and line.fsm_location_id.id)
            rec.fsm_location_ids = [(6, 0, location_ids)]
