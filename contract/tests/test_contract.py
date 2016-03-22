# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
import datetime

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestContract(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestContract, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.tax = self.env.ref('l10n_generic_coa.sale_tax_template')
        self.product.taxes_id = self.tax.ids
        self.product.description_sale = 'Test description sale'
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
        self.current_date = datetime.date.today()
        self.contract_daily = self.contract.copy()
        self.contract_daily.recurring_rule_type = 'daily'
        self.contract_weekly = self.contract.copy()
        self.contract_weekly.recurring_rule_type = 'weekly'

    def test_check_discount(self):
        with self.assertRaises(ValidationError):
            self.contract_line.write({'discount': 120})

    def test_contract(self):
        self.assertAlmostEqual(self.contract_line.price_subtotal, 50.0)
        res = self.contract_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.contract_line.price_unit = 100.0

        self.contract.partner_id = False
        with self.assertRaises(ValidationError):
            self.contract.recurring_create_invoice()
        self.contract.partner_id = self.partner.id

        self.contract.recurring_create_invoice()
        self.invoice_monthly = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(self.invoice_monthly)
        new_date = self.current_date + relativedelta(
            months=self.contract.recurring_interval)
        self.assertEqual(self.contract.recurring_next_date,
                         new_date.strftime('%Y-%m-%d'))

        self.inv_line = self.invoice_monthly.invoice_line_ids[0]
        self.assertAlmostEqual(self.inv_line.price_subtotal, 50.0)
        self.assertTrue(self.inv_line.invoice_line_tax_ids)

    def test_contract_daily(self):
        self.contract_daily.pricelist_id = False
        self.contract_daily.recurring_create_invoice()
        invoice_daily = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract_daily.id)])
        self.assertTrue(invoice_daily)
        new_date = self.current_date + relativedelta(
            days=self.contract_daily.recurring_interval)
        self.assertEqual(self.contract_daily.recurring_next_date,
                         new_date.strftime('%Y-%m-%d'))

    def test_contract_weekly(self):
        self.contract_weekly.recurring_create_invoice()
        invoices_weekly = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract_weekly.id)])
        self.assertTrue(invoices_weekly)
        new_date = self.current_date + relativedelta(
            weeks=self.contract_weekly.recurring_interval)
        self.assertEqual(self.contract_weekly.recurring_next_date,
                         new_date.strftime('%Y-%m-%d'))

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
