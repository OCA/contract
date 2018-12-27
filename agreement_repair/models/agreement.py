# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    repair_count = fields.Integer('# Repair Orders',
                                  compute='_compute_repair_count')

    @api.multi
    def _compute_repair_count(self):
        data = self.env['mrp.repair'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
        count_data = dict((item['agreement_id'][0],
                           item['agreement_id_count']) for item in data)
        for agreement in self:
            agreement.repair_count = count_data.get(agreement.id, 0)
