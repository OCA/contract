# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'

    agreement_id = fields.Many2one(
        'agreement',
        string='Agreement',
    )
    serviceprofile_id = fields.Many2one('agreement.serviceprofile',
                                        'Service Profile')
