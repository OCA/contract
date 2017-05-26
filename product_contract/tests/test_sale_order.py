# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
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
            'recurring_rule_type': 'yearly',
            'recurring_interval': 12345,
        })
        self.product.product_tmpl_id.is_contract = True
        self.product.product_tmpl_id.contract_template_id = self.contract.id

    def tearDown(self):
        self.env['account.analytic.account']._revert_method(
            'create',
        )

    def test_action_done(self):
        """ It should create a contract when the sale for a contract is set
        to done for the first time """
        self.env['account.analytic.account']._patch_method(
            'create', MagicMock()
        )
        self.sale.action_confirm()
        self.env['account.analytic.account'].create.assert_called_once_with({
            'name': '%s Contract' % self.sale.name,
            'partner_id': self.sale.partner_id.id,
            'contract_template_id': self.contract.id,
        })
