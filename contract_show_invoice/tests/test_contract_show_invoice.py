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
        self.invoice.journal_id.update_posted = True
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
             'invoice_line_tax_ids': [(4, self.env['account.tax'].search(
                 [('type_tax_use', '=', 'sale')], limit=1).id, 0)]
             })
        self.invoice.compute_taxes()
        self.invoice.action_invoice_open()

    def test_invoice_two_line(self):
        self.assertEqual(
            self.analytic_account.total_invoiced,
            self.invoice_line.price_subtotal,
            msg="Amount invoiced is different from single invoice line wich "
                "has analytic account")
        self.invoice.action_invoice_cancel()
        self.invoice.action_invoice_draft()
        self.invoice_line1 = self.env['account.invoice.line'].create(
            {'product_id': self.env.ref('product.product_product_2').id,
             'quantity': 2.0,
             'invoice_id': self.invoice.id,
             'account_analytic_id': False,
             'account_id': self.a_sale.id,
             'price_unit': 100.0,
             'name': 'Invoice line without analytic account',
             'invoice_line_tax_ids': [(4, self.env['account.tax'].search(
                 [('type_tax_use', '=', 'sale')], limit=1).id, 0)]
             })
        self.invoice.compute_taxes()
        self.invoice.action_invoice_open()
        self.assertFalse(self.invoice_line1.account_analytic_id,
                         msg="Invoice line has analytic account")
        self.assertEqual(len(self.invoice.analytic_account_ids), 1,
                         msg="Invoice lines with analytic account are more "
                             "than one")
        self.assertEqual(
            self.analytic_account.total_invoiced,
            self.invoice_line.price_subtotal,
            msg="Amount invoiced is different from invoice lines wich "
                "has analytic account")
