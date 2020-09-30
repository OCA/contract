# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo import fields
from odoo.tests.common import TransactionCase


def to_date(date):
    return fields.Date.to_date(date)


class TestContractSale(TransactionCase):
    # Use case : Prepare some data for current test case

    def setUp(self):
        super(TestContractSale, self).setUp()
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'pricelist for contract test',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'partner test contract',
            'property_product_pricelist': self.pricelist.id,
        })
        self.product_1 = self.env.ref('product.product_product_1')
        self.product_1.taxes_id += self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1
        )
        self.product_1.description_sale = 'Test description sale'
        self.line_template_vals = {
            'product_id': self.product_1.id,
            'name': 'Test Contract Template',
            'quantity': 1,
            'uom_id': self.product_1.uom_id.id,
            'price_unit': 100,
            'discount': 50,
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1,
        }
        self.template_vals = {
            'name': 'Test Contract Template',
            'contract_line_ids': [
                (0, 0, self.line_template_vals),
            ],
        }
        self.template = self.env['contract.template'].create(
            self.template_vals
        )
        # For being sure of the applied price
        self.env['product.pricelist.item'].create(
            {
                'pricelist_id': self.partner.property_product_pricelist.id,
                'product_id': self.product_1.id,
                'compute_price': 'formula',
                'base': 'list_price',
            }
        )
        self.contract = self.env['contract.contract'].create(
            {
                'name': 'Test Contract',
                'partner_id': self.partner.id,
                'pricelist_id': self.partner.property_product_pricelist.id,
                'type': 'sale',
                'sale_autoconfirm': False
            }
        )
        self.line_vals = {
            'contract_id': self.contract.id,
            'product_id': self.product_1.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': self.product_1.uom_id.id,
            'price_unit': 100,
            'discount': 50,
            'recurring_rule_type': 'monthly',
            'recurring_interval': 1,
            'date_start': '2020-01-01',
            'recurring_next_date': '2020-01-15',
        }
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        self.contract_line = self.env['contract.line'].create(
            self.line_vals
        )
        self.contract2 = self.env['contract.contract'].create(
            {
                'name': 'Test Contract 2',
                'type': 'sale',
                'partner_id': self.partner.id,
                'pricelist_id': self.partner.property_product_pricelist.id,
                'contract_type': 'purchase',
                'contract_line_ids': [
                    (
                        0,
                        0,
                        {
                            'product_id': self.product_1.id,
                            'name': 'Services from #START# to #END#',
                            'quantity': 1,
                            'uom_id': self.product_1.uom_id.id,
                            'price_unit': 100,
                            'discount': 50,
                            'recurring_rule_type': 'monthly',
                            'recurring_interval': 1,
                            'date_start': '2018-02-15',
                            'recurring_next_date': '2018-02-22',
                        },
                    )
                ],
            }
        )

    def test_check_discount(self):
        with self.assertRaises(ValidationError):
            self.contract_line.write({'discount': 120})

    def test_contract(self):
        recurring_next_date = to_date('2020-02-15')
        self.assertAlmostEqual(self.contract_line.price_subtotal, 50.0)
        res = self.contract_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.contract_line.price_unit = 100.0
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_sale()
        self.sale_monthly = self.contract._get_related_sales()
        self.assertTrue(self.sale_monthly)
        self.assertEqual(
            self.contract_line.recurring_next_date, recurring_next_date
        )
        self.order_line = self.sale_monthly.order_line[0]
        self.assertTrue(self.order_line.tax_id)
        self.assertAlmostEqual(self.order_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.user_id, self.sale_monthly.user_id)

    def test_contract_autoconfirm(self):
        recurring_next_date = to_date('2020-02-15')
        self.contract.sale_autoconfirm = True
        self.assertAlmostEqual(self.contract_line.price_subtotal, 50.0)
        res = self.contract_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.contract_line.price_unit = 100.0
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_sale()
        self.sale_monthly = self.contract._get_related_sales()
        self.assertTrue(self.sale_monthly)
        self.assertEqual(
            self.contract_line.recurring_next_date, recurring_next_date
        )
        self.order_line = self.sale_monthly.order_line[0]
        self.assertTrue(self.order_line.tax_id)
        self.assertAlmostEqual(self.order_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.user_id, self.sale_monthly.user_id)

    def test_onchange_contract_template_id(self):
        """It should change the contract values to match the template."""
        self.contract.contract_template_id = False
        self.contract._onchange_contract_template_id()
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        res = {
            'contract_line_ids':
            [(0, 0, {
                'product_id': self.product_1.id,
                'name': 'Test Contract Template',
                'quantity': 1,
                'uom_id': self.product_1.uom_id.id,
                'price_unit': 100,
                'discount': 50,
                'recurring_rule_type': 'yearly',
                'recurring_interval': 1,
            })]
        }
        del self.template_vals['name']
        self.assertDictEqual(res, self.template_vals)

    def test_contract_count_sale(self):
        self.contract.recurring_create_sale()
        self.contract.recurring_create_sale()
        self.contract.recurring_create_sale()
        self.contract._compute_sale_count()
        self.assertEqual(self.contract.sale_count, 3)

    def test_contract_count_sale_2(self):
        orders = self.env['sale.order']
        orders |= self.contract.recurring_create_sale()
        orders |= self.contract.recurring_create_sale()
        orders |= self.contract.recurring_create_sale()
        action = self.contract.action_show_sales()
        self.assertEqual(set(action['domain'][0][2]), set(orders.ids))

    def test_cron_recurring_create_sale(self):
        self.contract_line.date_start = '2020-01-01'
        self.contract_line.recurring_invoicing_type = 'post-paid'
        self.contract_line.date_end = '2020-03-15'
        self.contract_line._onchange_date_start()
        contracts = self.contract2
        for _i in range(10):
            contracts |= self.contract.copy({'type': 'sale'})
        self.env['contract.contract'].cron_recurring_create_sale()
        order_lines = self.env['sale.order.line'].search(
            [('contract_line_id', 'in',
              contracts.mapped('contract_line_ids').ids)]
        )
        self.assertEqual(
            len(contracts.mapped('contract_line_ids')),
            len(order_lines),
        )
