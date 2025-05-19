# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContract(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.contract.partner_id
        cls.transmit_method_mail = cls.env.ref("account_invoice_transmit_method.mail")
        cls.transmit_method_post = cls.env.ref("account_invoice_transmit_method.post")
        cls.partner.customer_invoice_transmit_method_id = cls.transmit_method_mail

    def test_onchange_partner_transmit_method(self):
        self.contract.partner_id = False
        self.assertFalse(self.contract.transmit_method_id)
        self.contract.partner_id = self.partner
        self.assertEqual(self.contract.transmit_method_id, self.transmit_method_mail)

    def test_create_invoice(self):
        self.assertFalse(self.contract.transmit_method_id)
        self.contract.transmit_method_id = self.transmit_method_post
        invoice = self.contract.recurring_create_invoice()
        self.assertEqual(invoice.transmit_method_id, self.transmit_method_post)
