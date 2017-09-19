# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_count = fields.Integer(
        compute='_compute_contract_count',
        string='# of Contracts',
    )
    contract_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='partner_id',
        string='Contracts',
    )

    @api.multi
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        contract_data = self.env['account.analytic.account'].read_group(
            domain=[('partner_id', 'child_of', self.ids),
                    ('recurring_invoices', '=', True)],
            fields=['partner_id'],
            groupby=['partner_id'])
        # read to keep the child/parent relation while aggregating the
        # read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([
            (m['partner_id'][0], m['partner_id_count']) for m in contract_data
        ])
        for partner in self:
            # let's obtain the partner id and all its child ids from the read
            # up there
            partner_ids = filter(
                lambda r: r['id'] == partner.id, partner_child_ids)[0]
            partner_ids = ([partner_ids.get('id')] +
                           partner_ids.get('child_ids'))
            # then we can sum for all the partner's child
            partner.contract_count = sum(
                mapped_data.get(child, 0) for child in partner_ids)
