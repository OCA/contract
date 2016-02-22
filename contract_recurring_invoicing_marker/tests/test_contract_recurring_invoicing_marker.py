# -*- coding: utf-8 -*-
# (c) 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestContractRecurringInvoicingMarker(common.TransactionCase):

    def setUp(self):
        super(TestContractRecurringInvoicingMarker, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test',
            'lang': 'en_US',
        })
        self.product = self.env.ref('product.product_product_consultant')
        self.uom = self.env.ref('product.product_uom_hour')
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': self.partner.id,
            'type': 'contract',
            'recurring_invoices': 1,
            'recurring_next_date': '2016-01-01',
            'recurring_rule_type': 'monthly',
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [
                (0, 0, {'quantity': 2.0,
                        'price_unit': 100.0,
                        'name': '#START# - #END#',
                        'product_id': self.product.id,
                        'uom_id': self.uom.id})],
        })

    def test_monthly_invoice_with_marker(self):
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertEqual(
            invoice.invoice_line[0].name, u'01/01/2016 - 01/31/2016')

    def test_daily_invoice_with_marker(self):
        self.contract.recurring_rule_type = 'daily'
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertEqual(
            invoice.invoice_line[0].name, u'01/01/2016 - 01/01/2016')

    def test_weekly_invoice_with_marker(self):
        self.contract.recurring_rule_type = 'weekly'
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertEqual(
            invoice.invoice_line[0].name, u'01/01/2016 - 01/07/2016')
