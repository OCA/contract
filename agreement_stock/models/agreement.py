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
        for ag_rec in self:
            ag_rec.picking_count = self.env['stock.picking'].search_count(
                [('agreement_id', 'in', ag_rec.ids)])

    @api.multi
    def _compute_move_count(self):
        for ag_rec in self:
            ag_rec.move_count = self.env['stock.move'].search_count(
                [('agreement_id', 'in', ag_rec.ids)])

    @api.multi
    def _compute_lot_count(self):
        for ag_rec in self:
            ag_rec.lot_count = self.env['stock.production.lot'].search_count(
                [('agreement_id', 'in', ag_rec.ids)])
