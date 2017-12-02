# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests
from ..hooks import post_init_hook


@odoo.tests.post_install(True)
@odoo.tests.at_install(False)
class TestContractPaymentInit(odoo.tests.HttpCase):

    def setUp(self):
        super(TestContractPaymentInit, self).setUp()

        self.payment_method = self.env['account.payment.method'].create({
            'name': 'Test Payment Method',
            'code': 'Test',
            'payment_type': 'inbound',
        })
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'Test payment mode',
            'active': True,
            'payment_method_id': self.payment_method.id,
            'bank_account_link': 'variable',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test contract partner',
            'customer_payment_mode_id': self.payment_mode,
        })
        self.product = self.env['product.product'].create({
            'name': 'Custom Service',
            'type': 'service',
            'uom_id': self.env.ref('product.product_uom_hour').id,
            'uom_po_id': self.env.ref('product.product_uom_hour').id,
            'sale_ok': True,
        })
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Maintenance of Servers',
        })
        company = self.env.ref('base.main_company')
        self.journal = self.env['account.journal'].create({
            'name': 'Sale Journal - Test',
            'code': 'HRTSJ',
            'type': 'sale',
            'company_id': company.id})

    def test_post_init_hook(self):
        contract = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': self.partner.id,
            'payment_mode_id': self.payment_mode.id,
        })
        self.assertEqual(contract.payment_mode_id,
                         self.payment_mode)

        contract.payment_mode_id = False
        self.assertEqual(contract.payment_mode_id.id, False)

        post_init_hook(self.cr, self.env)
        self.assertEqual(contract.payment_mode_id,
                         self.payment_mode)

    def test_contract_and_invoices(self):
        self.contract.write({'partner_id': self.partner.id})
        self.contract.on_change_partner_id()
        self.assertEqual(self.contract.payment_mode_id,
                         self.contract.partner_id.customer_payment_mode_id)
        self.contract.write({
            'recurring_invoices': True,
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [(0, 0, {
                'quantity': 2.0,
                'price_unit': 200.0,
                'name': 'Database Administration 25',
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
            })]
        })
        self.contract.recurring_create_invoice()
        new_invoice = self.env['account.invoice'].search([
            ('contract_id', '=', self.contract.id)
        ])
        self.assertEqual(new_invoice.partner_id, self.contract.partner_id)
        self.assertEqual(new_invoice.payment_mode_id,
                         self.contract.payment_mode_id)
        self.assertEqual(len(new_invoice.ids), 1)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.contract.payment_mode_id,
                         new_invoice.payment_mode_id)
