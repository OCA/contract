# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import ValidationError
from openerp.tests.common import SavepointCase


class TestContract(SavepointCase):
    # Use case : Prepare some data for current test case
    @classmethod
    def setUpClass(cls):
        super(TestContract, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner test',
            'customer': True,
        })
        cls.product = cls.env.ref('product.product_product_2')
        cls.product.description_sale = 'Test description sale'
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
        })
        cls.contract_line = cls.env['account.analytic.invoice.line'].create({
            'analytic_account_id': cls.contract.id,
            'product_id': cls.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': cls.product.uom_id.id,
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

        self.assertEqual(self.partner.contract_count, 1)
        self.contract.partner_id = False
        with self.assertRaises(ValidationError):
            self.contract.recurring_create_invoice()
        self.assertEqual(self.partner.contract_count, 0)
        self.contract.partner_id = self.partner.id
        self.assertEqual(self.partner.contract_count, 1)

        new_invoice = self.contract.recurring_create_invoice()
        self.assertTrue(new_invoice)
        self.assertEqual(self.contract.recurring_next_date, '2016-03-29')

        self.inv_line = new_invoice.invoice_line_ids[0]
        self.assertAlmostEqual(self.inv_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.partner_id.user_id, new_invoice.user_id)

    def test_contract_daily(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_rule_type = 'daily'
        self.contract.pricelist_id = False
        self.contract.cron_recurring_create_invoice()
        invoice_daily = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(invoice_daily)
        self.assertEqual(self.contract.recurring_next_date, '2016-03-01')

    def test_contract_weekly(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_rule_type = 'weekly'
        self.contract.recurring_invoicing_type = 'post-paid'
        new_invoice = self.contract.recurring_create_invoice()
        self.assertTrue(new_invoice)
        self.assertEqual(
            self.contract.recurring_next_date, '2016-03-07')

    def test_contract_yearly(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_rule_type = 'yearly'
        new_invoice = self.contract.recurring_create_invoice()
        self.assertTrue(new_invoice)
        self.assertEqual(
            self.contract.recurring_next_date, '2017-02-28')

    def test_contract_monthly_lastday(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_invoicing_type = 'post-paid'
        self.contract.recurring_rule_type = 'monthlylastday'
        new_invoice = self.contract.recurring_create_invoice()
        self.assertTrue(new_invoice)
        self.assertEqual(self.contract.recurring_next_date, '2016-03-31')

    def test_contract_monthly_lastday_prepaid(self):
        self.contract.recurring_next_date = '2016-02-25'
        self.contract.recurring_invoicing_type = 'pre-paid'
        self.contract.recurring_rule_type = 'monthlylastday'
        self.contract.recurring_create_invoice()
        new_invoice = self.contract.recurring_create_invoice()
        self.assertTrue(new_invoice)
        self.assertEqual(new_invoice.date_invoice, '2016-03-31')

    def test_onchange_partner_id(self):
        self.contract._onchange_partner_id()
        self.assertEqual(self.contract.pricelist_id,
                         self.contract.partner_id.property_product_pricelist)

    def test_onchange_recurring_invoices(self):
        self.contract.recurring_next_date = False
        self.contract._onchange_recurring_invoices()
        self.assertEqual(self.contract.recurring_next_date,
                         self.contract.date_start)

    def test_uom(self):
        uom_litre = self.env.ref('product.product_uom_litre')
        self.contract_line.uom_id = uom_litre.id
        self.contract_line._onchange_product_id()
        self.assertEqual(self.contract_line.uom_id,
                         self.contract_line.product_id.uom_id)

    def test_onchange_product_id(self):
        line = self.env['account.analytic.invoice.line'].new()
        res = line._onchange_product_id()
        self.assertFalse(res['domain']['uom_id'])

    def test_no_pricelist(self):
        self.contract.pricelist_id = False
        self.contract_line.quantity = 2
        self.assertAlmostEqual(self.contract_line.price_subtotal, 100.0)

    def test_check_journal(self):
        contract_no_journal = self.contract.copy()
        contract_no_journal.journal_id = False
        journal = self.env['account.journal'].search([('type', '=', 'sale')])
        journal.write({'type': 'general'})
        with self.assertRaises(ValidationError):
            contract_no_journal.recurring_create_invoice()

    def test_send_mail_contract(self):
        result = self.contract.action_contract_send()
        self.assertEqual(result['name'], 'Compose Email')
