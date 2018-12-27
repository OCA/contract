# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    agreement_id = fields.Many2one('agreement', 'Agreement')


class StockMove(models.Model):
    _inherit = "stock.move"

    agreement_id = fields.Many2one('agreement',
                                   related='picking_id.agreement_id',
                                   string='Agreement',
                                   store=True)


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    agreement_id = fields.Many2one('agreement', 'Agreement')
    serviceprofile_id = fields.Many2one('agreement.serviceprofile',
                                        'Service Profile')
