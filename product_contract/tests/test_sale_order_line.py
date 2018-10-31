# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from mock import MagicMock
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product = self.env.ref('product.product_product_1')
        self.sale = self.env.ref('sale.sale_order_2')
        self.contract = self.env['account.analytic.contract'].create({
            'name': 'Test',
        })
        self.product.product_tmpl_id.is_contract = True
        self.sale_order_line = self.sale.order_line.filtered(
            lambda l: l.product_id == self.product
        )

    def test_onchange_product(self):
        """ It should get recurrence invoicing info to the sale line from
        its product """
        self.assertEqual(
            self.sale_order_line.recurring_rule_type,
            self.product.recurring_rule_type
        )
        self.assertEqual(
            self.sale_order_line.recurring_interval,
            self.product.recurring_interval
        )
        self.assertEqual(
            self.sale_order_line.recurring_invoicing_type,
            self.product.recurring_invoicing_type
        )
