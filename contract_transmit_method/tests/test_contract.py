# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContract(TestContractBase):
    def setUp(self):
        super(TestContract, self).setUp()
        self.transmit_method_mail = self.env.ref(
            "account_invoice_transmit_method.mail"
        )
        self.transmit_method_post = self.env.ref(
            "account_invoice_transmit_method.post"
        )
        self.contract.partner_id.customer_invoice_transmit_method_id = (
            self.transmit_method_mail
        )

    def test_onchange_partner_transmit_method(self):
        self.assertFalse(self.contract.transmit_method_id)
        self.contract.onchange_partner_transmit_method()
        self.assertEqual(
            self.contract.transmit_method_id, self.transmit_method_mail
        )

    def test_create_invoice(self):
        self.assertFalse(self.contract.transmit_method_id)
        self.contract.transmit_method_id = self.transmit_method_post
        invoice = self.contract.recurring_create_invoice()
        self.assertEqual(invoice.transmit_method_id, self.transmit_method_post)
