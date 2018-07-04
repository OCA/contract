# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_contract_count = fields.Integer(
        string='Sale Contracts',
        compute='_compute_contract_count',
    )
    purchase_contract_count = fields.Integer(
        string='Purchase Contracts',
        compute='_compute_contract_count',
    )

    def _compute_contract_count(self):
        contract_model = self.env['account.analytic.account']
        today = fields.Date.today()
        fetch_data = contract_model.read_group([
            ('recurring_invoices', '=', True),
            ('partner_id', 'child_of', self.ids),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', today)],
            ['partner_id', 'contract_type'], ['partner_id', 'contract_type'],
            lazy=False)
        result = [[data['partner_id'][0], data['contract_type'],
                   data['__count']] for data in fetch_data]
        for partner in self:
            partner_child_ids = partner.child_ids.ids + partner.ids
            partner.sale_contract_count = sum([
                r[2] for r in result
                if r[0] in partner_child_ids and r[1] == 'sale'])
            partner.purchase_contract_count = sum([
                r[2] for r in result
                if r[0] in partner_child_ids and r[1] == 'purchase'])

    def act_show_contract(self):
        """ This opens contract view
            @return: the contract view
        """
        self.ensure_one()
        contract_type = self._context.get('contract_type')

        res = self._get_act_window_contract_xml(contract_type)
        res.update(
            context=dict(
                self.env.context,
                search_default_recurring_invoices=True,
                search_default_not_finished=True,
                search_default_partner_id=self.id,
                default_partner_id=self.id,
                default_recurring_invoices=True,
                default_pricelist_id=self.property_product_pricelist.id,
            ),
        )
        return res

    def _get_act_window_contract_xml(self, contract_type):
        if contract_type == 'purchase':
            return self.env['ir.actions.act_window'].for_xml_id(
                'contract', 'action_account_analytic_purchase_overdue_all')
        else:
            return self.env['ir.actions.act_window'].for_xml_id(
                'contract', 'action_account_analytic_sale_overdue_all')
