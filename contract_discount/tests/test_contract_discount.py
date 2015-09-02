# -*- coding: utf-8 -*-

import openerp.tests.common as common
from openerp.exceptions import ValidationError


def create_simple_contract(self, discount=0):

    partner_id = self.ref('base.res_partner_2')
    product_id = self.ref('product.product_product_consultant')
    uom_id = self.ref('product.product_uom_hour')

    line_values = [(0, 0, {'quantity': 2.0,
                           'price_unit': 100.0,
                           'discount': discount,
                           'name': 'Database Administration 25',
                           'product_id': product_id,
                           'uom_id': uom_id,
                           })]
    values = {
        'name': 'Maintenance of Servers',
        'partner_id': partner_id,
        'type': 'contract',
        'recurring_invoices': 1,
        'recurring_interval': 1,
        'recurring_invoice_line_ids': line_values,
    }

    return self.env['account.analytic.account']\
        .create(values)


class TestContractDiscount(common.TransactionCase):

    def setUp(self):
        super(TestContractDiscount, self).setUp()

    def test_create_simple_contract_without_discount(self):
        """Create contract without discount"""
        create_simple_contract(self)

    def test_create_simple_contract_with_discount(self):
        """Create contract with discount"""
        create_simple_contract(self, 50)
        create_simple_contract(self, 100)

    def test_create_simple_contract_with_negative_discount(self):
        """Create contract with negative discount"""
        create_simple_contract(self, -10)

    def test_discount_greater_than_100_error(self):
        """Create or write contract with greater than 100 discount"""
        contract = create_simple_contract(self)
        lines = contract.recurring_invoice_line_ids
        with self.assertRaises(ValidationError):
            lines.write({'discount': 110})

        with self.assertRaises(ValidationError):
            create_simple_contract(self, 150)
