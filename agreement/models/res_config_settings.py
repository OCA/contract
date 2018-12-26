# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_agreement_maintenance = fields.Boolean(
        string='Manage maintenance agreements and contracts')
    module_agreement_mrp = fields.Boolean(
        string='Link your manufacturing orders to an agreement.')
