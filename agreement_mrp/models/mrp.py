# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    agreement_id = fields.Many2one('agreement', 'Agreement')
    serviceprofile_id = fields.Many2one('agreement.serviceprofile',
                                        'Service Profile')
