# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import Form, TestContractBase


class TestContract(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.contract.partner_id
        cls.transmit_method_mail = cls.env.ref("account_invoice_transmit_method.mail")
        cls.transmit_method_post = cls.env.ref("account_invoice_transmit_method.post")
        cls.partner.customer_invoice_transmit_method_id = cls.transmit_method_mail
        cls.contract_template_id = cls.env["contract.template"].create(
            {
                "name": "Test Contract",
                "contract_type": "sale",
                "transmit_method_id": cls.transmit_method_mail.id,
            }
        )

    def test_onchange_partner_transmit_method(self):
        self.contract.partner_id = False
        self.assertFalse(self.contract.transmit_method_id)
        self.contract.partner_id = self.partner
        self.assertEqual(self.contract.transmit_method_id, self.transmit_method_mail)

    def test_create_invoice(self):
        self.contract.transmit_method_id = False
        self.assertFalse(self.contract.transmit_method_id)
        self.contract.transmit_method_id = self.transmit_method_post
        invoice = self.contract.recurring_create_invoice()
        self.assertEqual(invoice.transmit_method_id, self.transmit_method_post)

    def test_onchange_contract_template_id_method(self):
        with Form(self.contract) as contract_form:
            contract_form.contract_template_id = self.contract_template_id
            self.assertEqual(
                contract_form.transmit_method_id,
                self.contract_template_id.transmit_method_id,
            )
