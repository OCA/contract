# Copyright (C) 2019 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AgreementStage(models.Model):
    _inherit = 'agreement.stage'

    stage_type = fields.Selection([('agreement', 'Agreement'), ('serviceprofile', 'Service Profile')],
                                  string='Type', required=True)