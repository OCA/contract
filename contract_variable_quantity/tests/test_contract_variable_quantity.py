# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import exceptions


class TestContractVariableQuantity(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractVariableQuantity, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'recurring_invoices': True,
        })
        cls.formula = cls.env['contract.line.qty.formula'].create({
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
        cls.contract_line = cls.env['account.analytic.invoice.line'].create({
            'analytic_account_id': cls.contract.id,
            'product_id': cls.product.id,
            'name': 'Test',
            'qty_type': 'variable',
            'qty_formula_id': cls.formula.id,
            'quantity': 1,
            'uom_id': cls.product.uom_id.id,
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
