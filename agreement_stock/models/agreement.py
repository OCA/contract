# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    picking_count = fields.Integer('# Pickings',
                                   compute='_compute_picking_count')
    move_count = fields.Integer('# Moves', compute='_compute_move_count')
    lot_count = fields.Integer('# Lots/Serials', compute='_compute_lot_count')

    @api.multi
    def _compute_picking_count(self):
        data = self.env['stock.picking'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
        count_data = dict((item['agreement_id'][0],
                           item['agreement_id_count']) for item in data)
        for agreement in self:
            agreement.picking_count = count_data.get(agreement.id, 0)

    @api.multi
    def _compute_move_count(self):
        data = self.env['stock.move'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
        count_data = dict((item['agreement_id'][0],
                           item['agreement_id_count']) for item in data)
        for agreement in self:
            agreement.move_count = count_data.get(agreement.id, 0)

    @api.multi
    def _compute_lot_count(self):
        data = self.env['stock.production.lot'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
        count_data = dict((item['agreement_id'][0],
                           item['agreement_id_count']) for item in data)
        for agreement in self:
            agreement.lot_count = count_data.get(agreement.id, 0)
