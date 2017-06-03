# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestContractMandate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractMandate, cls).setUpClass()
        cls.payment_method = cls.env['account.payment.method'].create({
            'name': 'Test SDD',
            'code': 'test_code_sdd',
            'payment_type': 'inbound',
            'mandate_required': True,
        })
        cls.payment_mode = cls.env['account.payment.mode'].create({
            'name': 'Test payment mode',
            'bank_account_link': 'variable',
            'payment_method_id': cls.payment_method.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'customer': True,
            'name': 'Test Customer',
            'customer_payment_mode_id': cls.payment_mode.id,
        })
        cls.partner_bank = cls.env['res.partner.bank'].create({
            'acc_number': '1234',
            'partner_id': cls.partner.id,
        })
        cls.mandate = cls.env['account.banking.mandate'].create({
            'partner_id': cls.partner.id,
            'partner_bank_id': cls.partner_bank.id,
            'signature_date': '2017-01-01',
        })
        cls.uom = cls.env.ref('product.product_uom_hour')
        cls.product = cls.env['product.product'].create({
            'name': 'Custom Service',
            'type': 'service',
            'uom_id': cls.uom.id,
            'uom_po_id': cls.uom.id,
            'sale_ok': True,
            'taxes_id': [(6, 0, [])],
        })
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': cls.partner.id,
            'recurring_invoices': True,
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [(0, 0, {
                'quantity': 2.0,
                'price_unit': 200.0,
                'name': 'Test contract line',
                'product_id': cls.product.id,
                'uom_id': cls.product.uom_id.id,
            })],
            'payment_mode_id': cls.payment_mode.id,
            'mandate_id': cls.mandate.id,
        })

    def test_contract_mandate(self):
        new_invoice = self.contract.recurring_create_invoice()
        self.assertEqual(new_invoice.mandate_id, self.mandate)

    def test_contract_not_mandate(self):
        self.contract.mandate_id = False
        self.mandate2 = self.mandate.copy({
            'unique_mandate_reference': 'BM0000XX2',
        })
        self.mandate2.validate()
        self.mandate.state = 'expired'
        new_invoice = self.contract.recurring_create_invoice()
        self.assertEqual(new_invoice.mandate_id, self.mandate2)

    def test_contract_mandate_default(self):
        self.payment_mode.mandate_required = False
        self.contract.mandate_id = False
        new_invoice = self.contract.recurring_create_invoice()
        self.assertFalse(new_invoice.mandate_id)
