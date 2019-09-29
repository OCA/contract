# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    agreement_id = fields.Many2one('agreement', readonly=True)

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        for values in vals_list:
            so_id = values.get('sale_id')
            if so_id:
                agreement = self.env['sale.order'].browse(so_id).agreement_id
                values['agreement_id'] = agreement.id
        res = super().create(vals_list)
        return res
