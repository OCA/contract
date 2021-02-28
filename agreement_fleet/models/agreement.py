# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):

    _inherit = 'agreement'

    vehicle_ids = fields.One2many(
        'fleet.vehicle',
        'agreement_id',
        string="Vehicles"
    )

    vehicle_count = fields.Integer(
        compute='_compute_vehicle_count',
        string='# Vehicles'
    )

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for rec in self:
            rec.vehicle_count = len(
                rec.vehicle_ids)

    @api.multi
    def action_view_vehicle(self):
        for agreement in self:
            action = self.env.ref(
                'fleet.fleet_vehicle_action').read()[0]
            action['context'] = {}
            if len(self.vehicle_ids) == 1:
                action['views'] = [(
                    self.env.ref('fleet.fleet_vehicle_view_form').id,
                    'form')]
                action['res_id'] = self.vehicle_ids.ids[0]
            else:
                action['domain'] = [('id', 'in', self.vehicle_ids.ids)]
            return action
