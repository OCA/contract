# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractMandate(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_method = cls.env["account.payment.method"].create(
            {
                "name": "Test SDD",
                "code": "test_code_sdd",
                "payment_type": "inbound",
                "mandate_required": True,
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "bank_account_link": "variable",
                "payment_method_id": cls.payment_method.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Customer", "customer_payment_mode_id": cls.payment_mode.id}
        )
        cls.partner_bank = cls.env["res.partner.bank"].create(
            {"acc_number": "1234", "partner_id": cls.partner.id}
        )
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_id": cls.partner.id,
                "partner_bank_id": cls.partner_bank.id,
                "signature_date": "2017-01-01",
            }
        )
        cls.contract_with_mandate = cls.contract2.copy(
            {
                "partner_id": cls.partner.id,
                "payment_mode_id": cls.payment_mode.id,
                "mandate_id": cls.mandate.id,
            }
        )

    def test_contract_mandate(self):
        new_invoice = self.contract_with_mandate.recurring_create_invoice()
        self.assertEqual(new_invoice.mandate_id, self.mandate)

    def test_contract_not_mandate(self):
        self.contract_with_mandate.mandate_id = False
        self.mandate2 = self.mandate.copy({"unique_mandate_reference": "BM0000XX2"})
        self.mandate2.validate()
        self.mandate.state = "expired"
        new_invoice = self.contract_with_mandate.recurring_create_invoice()
        self.assertEqual(new_invoice.mandate_id, self.mandate2)

    def test_contract_mandate_default(self):
        self.payment_mode.payment_method_id.mandate_required = False
        self.contract_with_mandate.mandate_id = False
        new_invoice = self.contract_with_mandate.recurring_create_invoice()
        self.assertFalse(new_invoice.mandate_id)
