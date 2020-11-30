# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase


class TestContractMandate(HttpCase):

    def setUp(self):
        super(TestContractMandate, self).setUp()
        self.payment_method = self.env['account.payment.method'].create({
            'name': 'Test SDD',
            'code': 'test_code_sdd',
            'payment_type': 'inbound',
            'mandate_required': True,
        })
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'Test payment mode',
            'bank_account_link': 'variable',
            'payment_method_id': self.payment_method.id,
        })
        self.partner = self.env['res.partner'].create({
            'customer': True,
            'name': 'Test Customer',
            'customer_payment_mode_id': self.payment_mode.id,
        })
        self.partner_bank = self.env['res.partner.bank'].create({
            'acc_number': '1234',
            'partner_id': self.partner.id,
        })
        self.mandate = self.env['account.banking.mandate'].create({
            'partner_id': self.partner.id,
            'partner_bank_id': self.partner_bank.id,
            'signature_date': '2017-01-01',
        })
        self.uom = self.env.ref('product.product_uom_hour')
        self.product = self.env['product.product'].create({
            'name': 'Custom Service',
            'type': 'service',
            'uom_id': self.uom.id,
            'uom_po_id': self.uom.id,
            'sale_ok': True,
            'taxes_id': [(6, 0, [])],
        })
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': self.partner.id,
            'recurring_invoices': True,
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [(0, 0, {
                'quantity': 2.0,
                'price_unit': 200.0,
                'name': 'Test contract line',
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
            })],
            'payment_mode_id': self.payment_mode.id,
            'mandate_id': self.mandate.id,
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
