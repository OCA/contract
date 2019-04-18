# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    task_count = fields.Integer('# Tasks',
                                compute='_compute_task_count')

    @api.multi
    def _compute_task_count(self):
        for ag in self:
            count = self.env['project.task'].search_count(
                [('agreement_id', '=', ag.id)])
            ag.task_count = count
