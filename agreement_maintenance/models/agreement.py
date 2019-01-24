# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    mr_count = fields.Integer('# Maintenance Requests',
                              compute='_compute_mr_count')

    @api.multi
    def _compute_mr_count(self):
        data = self.env['maintenance.request'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
        count_data = dict((item['agreement_id'][0],
                           item['agreement_id_count']) for item in data)
        for agreement in self:
            agreement.mr_count = count_data.get(agreement.id, 0)
