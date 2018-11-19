# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
import odoo
from odoo import exceptions


@odoo.tests.at_install(False)
@odoo.tests.post_install(True)
class TestContractVariableDiscount(TransactionCase):
    def setUp(self):
        super(TestContractVariableDiscount, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.product.taxes_id += self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1)
        self.product.description_sale = 'Test description sale'
        self.template_vals = {
            'recurring_rule_type': 'yearly',
            'recurring_interval': 12345,
            'name': 'Test Contract Template',
        }
        self.template = self.env['account.analytic.contract'].create(
            self.template_vals,
        )
        # For being sure of the applied price
        self.env['product.pricelist.item'].create({
            'applied_on': '0_product_variant',
            'pricelist_id': self.partner.property_product_pricelist.id,
            'product_id': self.product.id,
            'compute_price': 'fixed',
            'fixed_price': 1100,
        })
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
            'contract_template_id': self.template.id,
        })
        self.formula = self.env['contract.line.discount.formula'].create({
            'name': 'Test formula',
            # For testing each of the possible variables
            'code': 'result = 15',
        })
        self.line_vals = {
            'analytic_account_id': self.template.id,
            'product_id': self.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': self.product.uom_id.id,
            'price_unit': 100,
            'discount_type': 'variable',
            'discount_formula_id': self.formula.id,
        }
        self.acct_line = self.env['account.analytic.contract.line'].create(
            self.line_vals,
        )

    def test_check_invalid_code(self):
        with self.assertRaises(exceptions.ValidationError):
            self.formula.code = "student"

    def test_check_no_return_value(self):
        with self.assertRaises(exceptions.ValidationError):
            self.formula.code = "partner.id"

    def test_check_variable_discount(self):
        self.contract._onchange_contract_template_id()
        self.contract._create_invoice()
        invoice = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice.invoice_line_ids[0].discount, 15)
