# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    agreement_id = fields.Many2one('agreement', 'Agreement')
    serviceprofile_id = fields.Many2one('agreement.serviceprofile',
                                        'Service Profile')
