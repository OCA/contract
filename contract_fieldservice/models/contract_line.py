# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ContractLine(models.Model):
    _inherit = 'contract.line'

    fsm_location_id = fields.Many2one(
        'fsm.location', string='Service To', required=True, index=True
    )
