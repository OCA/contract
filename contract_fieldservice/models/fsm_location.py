# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FsmLocation(models.Model):
    _inherit = 'fsm.location'

    contract_ids = fields.Many2many(
        'contract.contract', 'contract_fsm_location',
        'fsm_location_id', 'contract_id', string='Contracts',
        readonly=True, store=True, index=True)
