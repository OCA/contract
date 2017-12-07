# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestContractSale(TransactionCase):
    # Use case : Prepare some data for current test case

    def setUp(self):
        super(TestContractSale, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.product.taxes_id += self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1)
        self.product.description_sale = 'Test description sale'
        self.template_vals = {
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1,
            'name': 'Test Contract Template',
            'type': 'sale',
            'sale_autoconfirm': False
        }
        self.template = self.env['account.analytic.contract'].create(
            self.template_vals,
        )
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
        })
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        self.contract_line = self.env['account.analytic.invoice.line'].create({
            'analytic_account_id': self.contract.id,
            'product_id': self.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': self.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        })

    def test_check_discount(self):
        with self.assertRaises(ValidationError):
            self.contract_line.write({'discount': 120})

    def test_contract(self):
        self.assertAlmostEqual(self.contract_line.price_subtotal, 50.0)
        res = self.contract_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.contract_line.price_unit = 100.0
        self.contract.recurring_create_sale()
        self.sale_monthly = self.env['sale.order'].search(
            [('project_id', '=', self.contract.id),
             ('state', '=', 'draft')])
        self.assertTrue(self.sale_monthly)
        self.assertEqual(self.contract.recurring_next_date, '2017-02-28')
        self.sale_line = self.sale_monthly.order_line[0]
        self.assertAlmostEqual(self.sale_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.partner_id.user_id,
                         self.sale_monthly.user_id)

    def test_contract_autoconfirm(self):
        self.contract.sale_autoconfirm = True
        self.assertAlmostEqual(self.contract_line.price_subtotal, 50.0)
        res = self.contract_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.contract_line.price_unit = 100.0
        self.contract.recurring_create_sale()
        self.sale_monthly = self.env['sale.order'].search(
            [('project_id', '=', self.contract.id),
             ('state', '=', 'sale')])
        self.assertTrue(self.sale_monthly)
        self.assertEqual(self.contract.recurring_next_date, '2017-02-28')

        self.sale_line = self.sale_monthly.order_line[0]
        self.assertAlmostEqual(self.sale_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.partner_id.user_id,
                         self.sale_monthly.user_id)

    def test_onchange_contract_template_id(self):
        """ It should change the contract values to match the template. """
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        res = {
            'recurring_rule_type': self.contract.recurring_rule_type,
            'recurring_interval': self.contract.recurring_interval,
            'type': 'sale',
            'sale_autoconfirm': False
        }
        del self.template_vals['name']
        self.assertDictEqual(res, self.template_vals)
