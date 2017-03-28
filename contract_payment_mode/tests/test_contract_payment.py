# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from ..hooks import post_init_hook


class TestContractPaymentInit(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractPaymentInit, cls).setUpClass()

        cls.payment_method = cls.env.ref(
            'account.account_payment_method_manual_in')
        cls.payment_mode = cls.env.ref(
            'account_payment_mode.payment_mode_inbound_ct1')
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test contract partner',
            'customer_payment_mode_id': cls.payment_mode,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Custom Service',
            'type': 'service',
            'uom_id': cls.env.ref('product.product_uom_hour').id,
            'uom_po_id': cls.env.ref('product.product_uom_hour').id,
            'sale_ok': True,
        })
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Maintenance of Servers',
        })

    def _contract_payment_mode_id(self, contract_id):
        contract = self.env['account.analytic.account'].search([
            ('id', '=', contract_id),
        ])
        return contract.payment_mode_id.id

    def test_post_init_hook(self):
        contract = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': self.partner.id,
            'payment_mode_id': self.payment_mode.id,
        })
        self.assertEqual(self._contract_payment_mode_id(contract.id),
                         self.payment_mode.id)

        contract.payment_mode_id = False
        self.assertEqual(self._contract_payment_mode_id(contract.id), False)

        post_init_hook(self.cr, self.env)
        self.assertEqual(self._contract_payment_mode_id(contract.id),
                         self.payment_mode.id)

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
        res = self.contract._prepare_invoice_data(self.contract)
        self.assertEqual(res.get('partner_id'), self.contract.partner_id.id)
        self.assertEqual(res.get('payment_mode_id'),
                         self.contract.payment_mode_id.id)
        self.contract.recurring_create_invoice()
        new_invoice = self.env['account.invoice'].search([
            ('contract_id', '=', self.contract.id)
        ])
        self.assertEqual(len(new_invoice.ids), 1)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.contract.payment_mode_id,
                         new_invoice.payment_mode_id)
