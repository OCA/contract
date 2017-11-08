# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_count = fields.Integer(
        string='Contracts',
        compute='_compute_contract_count',
    )

    def _compute_contract_count(self):
        Contract = self.env['account.analytic.account']
        today = fields.Date.today()
        for partner in self:
            partner.contract_count = Contract.search_count([
                ('recurring_invoices', '=', True),
                ('partner_id', '=', partner.id),
                ('date_start', '<=', today),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', today),
            ])

    def act_show_contract(self):
        """ This opens contract view
            @return: the contract view
        """
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'contract', 'action_account_analytic_overdue_all')
        res.update(
            context=dict(
                self.env.context,
                search_default_recurring_invoices=True,
                search_default_not_finished=True,
                default_partner_id=self.id,
                default_recurring_invoices=True,
            ),
            domain=[('partner_id', '=', self.id)],
        )
        return res
