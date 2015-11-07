# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestContractRecurringPlans(common.TransactionCase):

    def setUp(self):
        super(TestContractRecurringPlans, self).setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test'})
        self.product = self.env.ref('product.product_product_consultant')
        self.uom = self.env.ref('product.product_uom_hour')
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': self.partner.id,
            'type': 'contract',
            'recurring_invoices': 1,
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [
                (0, 0, {'quantity': 2.0,
                        'price_unit': 100.0,
                        'name': 'Test',
                        'product_id': self.product.id,
                        'uom_id': self.uom.id})],
        })
        plan = self.env['account.analytic.plan'].create({'name': 'Test'})
        self.analytics = self.env['account.analytic.plan.instance'].create(
            {'plan_id': plan.id})

    def test_invoice_without_plans(self):
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertEqual(
            invoice.invoice_line[0].account_analytic_id, self.contract)

    def test_invoice_with_plans(self):
        self.contract.recurring_invoice_line_ids.analytics_id = (
            self.analytics.id)
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertFalse(invoice.invoice_line[0].account_analytic_id)
        self.assertEqual(
            invoice.invoice_line[0].analytics_id, self.analytics)
