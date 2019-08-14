# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase


class TestContractShowInvoice(TransactionCase):
    def setUp(self):
        super(TestContractShowInvoice, self).setUp()
        self.analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test contract show invoice',
        })
        self.invoice = self.env['account.invoice'].create(
            {'partner_id': self.env.ref('base.res_partner_2').id,
             'type': 'out_invoice',
             })
        self.invoice._onchange_partner_id()
        self.a_sale = self.env['account.account'].search([
            ('user_type_id', '=',
                self.env.ref('account.data_account_type_revenue').id)
        ], limit=1)
        self.invoice_line = self.env['account.invoice.line'].create(
            {'product_id': self.env.ref('product.product_product_2').id,
             'quantity': 1.0,
             'invoice_id': self.invoice.id,
             'account_analytic_id': self.analytic_account.id,
             'account_id': self.a_sale.id,
             'price_unit': 50.0,
             'name': 'Invoice line with analytic account',
             })
        self.invoice_line._onchange_product_id()

    def test_contract_show_invoice(self):
        self.assertEqual(len(self.invoice.analytic_account_ids), 1)

    def test_contract_total_invoiced(self):
        self.assertEqual(self.invoice.amount_total,
                         self.analytic_account.total_invoiced)

    def test_invoice_two_line(self):
        self.invoice_line1 = self.env['account.invoice.line'].create(
            {'product_id': self.env.ref('product.product_product_2').id,
             'quantity': 2.0,
             'invoice_id': self.invoice.id,
             'account_analytic_id': False,
             'account_id': self.a_sale.id,
             'price_unit': 100.0,
             'name': 'Invoice line without analytic account',
             })
        self.assertFalse(self.invoice_line1.account_analytic_id)
        self.assertNotEqual(
            self.analytic_account.total_invoiced, self.invoice.amount_total,
            msg="Amount invoiced is from total of invoice, even if only 1 line"
                " has analytic account")
