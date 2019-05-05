# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,protected-access,invalid-name
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product = self.env.ref('product.product_product_1')
        self.sale = self.env.ref('sale.sale_order_2')
        self.contract = self.env['account.analytic.contract'].create({
            'name': 'Test',
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1})
        self.product.product_tmpl_id.is_contract = True
        self.product.product_tmpl_id.contract_template_id = self.contract.id

    def test_action_confirm(self):
        """Contract should be created when sale is confirmed."""
        self.sale.action_confirm()
        contract_model = self.env['account.analytic.account']
        product_contract = contract_model.search([
            ('recurring_invoices', '=', True),
            ('partner_id', '=', self.sale.partner_id.id),
            ('contract_template_id', '=', self.contract.id)], limit=1)
        self.assertTrue(product_contract)
