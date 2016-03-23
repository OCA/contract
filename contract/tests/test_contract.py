# -*- coding: utf-8 -*-
# © 2016 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestContract(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestContract, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
        })
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

    def test_create_invoice(self):
        self.contract.recurring_create_invoice()
        self.invoice = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(self.invoice)

        self.inv_line = self.invoice.invoice_line_ids[0]
        self.assertAlmostEqual(self.inv_line.price_subtotal, 50.0)
