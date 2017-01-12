# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.product = self.env.ref(
            'product.product_product_4_product_template'
        )
        self.contract = self.env['account.analytic.contract'].create({
            'name': 'Test',
            'recurring_rule_type': 'yearly',
            'recurring_interval': 12345,
        })

    def test_change_is_contract(self):
        """ It should verify that the contract_template_id is removed
        when is_contract is False """
        self.product.is_contract = True
        self.product.contract_template_id = self.contract.id
        self.product.is_contract = False
        self.product._change_is_contract()
        self.assertEquals(
            len(self.product.contract_template_id),
            0
        )
