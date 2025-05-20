# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractAutoValidate(TestContractBase):
    def test_contract_invoice_auto_validate_1(self):
        contracts = self.contract2
        invoice = contracts._recurring_create_invoice()
        self.assertTrue(invoice.exists())
        self.assertEqual(invoice.state, "draft")

    def test_contract_invoice_auto_validate_2(self):
        contracts = self.contract2
        contracts.company_id.auto_post_contract_invoice = True
        invoice = contracts._recurring_create_invoice()
        self.assertTrue(invoice.exists())
        self.assertEqual(invoice.state, "posted")
