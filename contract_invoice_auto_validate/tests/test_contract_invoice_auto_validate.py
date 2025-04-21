# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractAutoValidate(TestContractBase):
    def test_contract_invoice_auto_validate(self):
        contracts = self.contract2
        invoice = contracts._recurring_create_invoice()
        self.assertEqual(invoice.state, "posted")
