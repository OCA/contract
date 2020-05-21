# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    sale_ids = fields.One2many(
        'sale.order', 'agreement_id', string='Sale Orders', readonly=True)
    sale_count = fields.Integer(
        compute='_compute_sale_count', string='# of Sale Orders')

    def _compute_sale_count(self):
        rg_res = self.env['sale.order'].read_group(
            [
                ('agreement_id', 'in', self.ids),
                ('state', 'not in', ('draft', 'sent', 'cancel')),
            ],
            ['agreement_id'], ['agreement_id'])
        mapped_data = dict(
            [(x['agreement_id'][0], x['agreement_id_count']) for x in rg_res])
        for agreement in self:
            agreement.sale_count = mapped_data.get(agreement.id, 0)
