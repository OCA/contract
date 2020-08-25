# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    serviceprofile_ids = fields.One2many('agreement.serviceprofile',
                                         'agreement_id',
                                         string="Service Profiles",
                                         copy=True)
