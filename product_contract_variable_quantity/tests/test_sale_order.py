# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product1 = self.env.ref('product.product_product_1')
        self.sale = self.env.ref('sale.sale_order_2')
        self.contract_template1 = self.env['account.analytic.contract'].create(
            {'name': 'Template 1'}
        )
        self.formula = self.env['contract.line.qty.formula'].create(
            {
                'name': 'Test formula',
                # For testing each of the possible variables
                'code': 'env["res.users"]\n'
                'context.get("lang")\n'
                'user.id\n'
                'line.qty_type\n'
                'contract.id\n'
                'invoice.id\n'
                'result = 12',
            }
        )
        self.product1.write(
            {
                'is_contract': True,
                'contract_template_id': self.contract_template1.id,
                'qty_formula_id': self.formula.id,
                'qty_type': 'variable',
            }
        )
        self.order_line1 = self.sale.order_line.filtered(
            lambda l: l.product_id == self.product1
        )

    def test_onchange_product_id(self):
        self.order_line1.onchange_product()
        self.assertEqual(
            self.order_line1.qty_formula_id, self.product1.qty_formula_id
        )
        self.assertEqual(self.order_line1.qty_type, self.product1.qty_type)

    def test_action_confirm(self):
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        contract = self.order_line1.contract_id
        contract_line = contract.recurring_invoice_line_ids.filtered(
            lambda line: line.product_id == self.product1
        )
        self.assertEqual(
            contract_line.qty_formula_id, self.product1.qty_formula_id
        )
        self.assertEqual(contract_line.qty_type, self.product1.qty_type)
