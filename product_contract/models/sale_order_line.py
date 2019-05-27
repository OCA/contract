# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,protected-access
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract')

    @api.multi
    def create_contract(self):
        """Create contract for sale order line.

        Should be called on confirmation of sale order.
        """
        for line in self.filtered('product_id.is_contract'):
            contract_vals = line._prepare_contract_vals()
            contract = self.env['account.analytic.account'].create(
                contract_vals)
            line.contract_id = contract.id

    @api.multi
    def _prepare_contract_vals(self):
        """Prepare values to create contract from template."""
        self.ensure_one()
        contract_tmpl = self.product_id.contract_template_id
        order = self.order_id
        contract = self.env['account.analytic.account'].new({
            'name': '%s Contract' % order.name,
            'partner_id': order.partner_id.id,
            'contract_template_id': contract_tmpl.id,
            'recurring_invoices': True})
        contract._onchange_contract_template_id()
        return contract._convert_to_write(contract._cache)
