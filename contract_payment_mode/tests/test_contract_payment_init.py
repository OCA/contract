# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from ..hooks import post_init_hook


class TestContractPaymentInit(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestContractPaymentInit, self).setUp()
        self.payment_mode = self.env.ref('account_payment.payment_mode_1')
        self.partner = self.env['res.partner'].create({
            'name': 'Test contract partner',
            'customer_payment_mode': self.payment_mode.id,
        })

    def _contract_payment_mode_id(self, contract_id):
        contract = self.env['account.analytic.account'].search([
            ('id', '=', contract_id),
        ])
        return contract.payment_mode_id.id

    def test_post_init_hook(self):
        contract = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'type': 'contract',
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
