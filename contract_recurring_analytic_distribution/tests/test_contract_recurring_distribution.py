# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestContractRecurringDistribution(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractRecurringDistribution, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.account1 = cls.env['account.analytic.account'].create({
            'name': 'Test account #1',
        })
        cls.account2 = cls.env['account.analytic.account'].create({
            'name': 'Test account #2',
        })
        cls.uom = cls.env.ref('product.product_uom_hour')
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': cls.partner.id,
            'type': 'contract',
            'recurring_invoices': 1,
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [
                (0, 0, {'quantity': 2.0,
                        'price_unit': 100.0,
                        'name': 'Test',
                        'product_id': cls.product.id,
                        'uom_id': cls.uom.id})],
        })
        cls.distribution = cls.env['account.analytic.distribution'].create({
            'name': 'Test distribution',
            'rule_ids': [
                (0, 0, {
                    'sequence': 10,
                    'percent': 75.00,
                    'analytic_account_id': cls.account1.id,
                }),
                (0, 0, {
                    'sequence': 20,
                    'percent': 25.00,
                    'analytic_account_id': cls.account2.id,
                }),
            ]
        })

    def test_invoice_without_distribution(self):
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertEqual(
            invoice.invoice_line_ids[0].account_analytic_id, self.contract)

    def test_invoice_with_distribution(self):
        self.contract.recurring_invoice_line_ids.analytic_distribution_id = (
            self.distribution.id)
        self.contract.recurring_create_invoice()
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        self.assertFalse(invoice.invoice_line_ids[0].account_analytic_id)
        self.assertEqual(
            invoice.invoice_line_ids[0].analytic_distribution_id,
            self.distribution)
