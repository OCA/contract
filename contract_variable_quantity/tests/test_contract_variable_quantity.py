# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests
from odoo import exceptions


@odoo.tests.at_install(False)
@odoo.tests.post_install(True)
class TestContractVariableQuantity(odoo.tests.HttpCase):
    def setUp(self):
        super(TestContractVariableQuantity, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        self.product = self.env['product.product'].create({
            'name': 'Test product',
        })
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
        })
        self.formula = self.env['contract.line.qty.formula'].create({
            'name': 'Test formula',
            # For testing each of the possible variables
            'code': 'env["res.users"]\n'
                    'context.get("lang")\n'
                    'user.id\n'
                    'line.qty_type\n'
                    'contract.id\n'
                    'invoice.id\n'
                    'result = 12',
        })
        self.contract_line = self.env['account.analytic.invoice.line'].create({
            'analytic_account_id': self.contract.id,
            'product_id': self.product.id,
            'name': 'Test',
            'qty_type': 'variable',
            'qty_formula_id': self.formula.id,
            'quantity': 1,
            'uom_id': self.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        })

    def test_check_invalid_code(self):
        with self.assertRaises(exceptions.ValidationError):
            self.formula.code = "sdsds"

    def test_check_no_return_value(self):
        with self.assertRaises(exceptions.ValidationError):
            self.formula.code = "user.id"

    def test_check_variable_quantity(self):
        self.contract._create_invoice()
        invoice = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 12)
