# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product1 = self.env.ref('product.product_product_1')
        self.product2 = self.env.ref('product.product_product_2')
        self.sale = self.env.ref('sale.sale_order_2')
        self.contract_template1 = self.env['account.analytic.contract'].create(
            {'name': 'Template 1'}
        )
        self.contract_template2 = self.env['account.analytic.contract'].create(
            {'name': 'Template 2'}
        )
        self.product1.write(
            {
                'is_contract': True,
                'contract_template_id': self.contract_template1.id,
            }
        )
        self.product2.write(
            {
                'is_contract': True,
                'contract_template_id': self.contract_template2.id,
            }
        )
        self.order_line1 = self.sale.order_line.filtered(
            lambda l: l.product_id == self.product1
        )

    def test_compute_is_contract(self):
        """Sale Order should have is_contract true if one of its lines is
        contract"""
        self.assertTrue(self.sale.is_contract)

    def test_action_confirm(self):
        """ It should create a contract for each contract template used in
        order_line """
        self.sale.action_confirm()
        contracts = self.sale.order_line.mapped('contract_id')
        self.assertEqual(len(contracts), 2)
        self.assertEqual(
            self.order_line1.contract_id.contract_template_id,
            self.contract_template1,
        )

    def test_sale_contract_count(self):
        """It should count contracts as many different contract template used
        in order_line"""
        self.sale.action_confirm()
        self.assertEqual(self.sale.contract_count, 2)

    def test_onchange_product(self):
        """ It should get recurrence invoicing info to the sale line from
        its product """
        self.assertEqual(
            self.order_line1.recurring_rule_type,
            self.product1.recurring_rule_type,
        )
        self.assertEqual(
            self.order_line1.recurring_interval,
            self.product1.recurring_interval,
        )
        self.assertEqual(
            self.order_line1.recurring_invoicing_type,
            self.product1.recurring_invoicing_type,
        )

    def test_check_contract_sale_partner(self):
        contract2 = self.env['account.analytic.account'].create(
            {
                'name': 'Contract',
                'contract_template_id': self.contract_template2.id,
                'partner_id': self.sale.partner_id.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = contract2

    def test_check_contract_sale_contract_template(self):
        contract1 = self.env['account.analytic.account'].create(
            {
                'name': 'Contract',
                'contract_template_id': self.contract_template1.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = contract1
