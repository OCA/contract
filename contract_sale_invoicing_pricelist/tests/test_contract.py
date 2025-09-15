from odoo.tests import tagged

from odoo.addons.contract.tests.test_contract import TestContractBase


@tagged("post_install", "-at_install")
class TestContract(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super(TestContract, cls).setUpClass()

    def test_contract_invoice_pricelist(self):
        """New method to test the pricelist value in invoice created from contract."""
        self.contract.recurring_create_invoice()
        self.invoice_monthly = self.contract._get_related_invoices()
        # Assert that the invoice pricelist is same as the contract pricelist.
        self.assertEqual(
            self.contract.pricelist_id.id,
            self.invoice_monthly.pricelist_id.id,
            "Pricelist in invoice is not same as the contract.",
        )
