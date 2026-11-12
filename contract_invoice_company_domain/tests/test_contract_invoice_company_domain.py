# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractInvoiceCompanyDomain(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.contract.company_id
        cls.company2 = cls.env["res.company"].create({"name": "Second Company"})
        cls.contract_company2 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract Company 2",
                "company_id": cls.company2.id,
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
            }
        )

    def _contracts_to_invoice(self):
        model = self.env["contract.contract"]
        return model.search(model._get_contracts_to_invoice_domain())

    def test_enabled_no_domain_selects_contract(self):
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = False
        self.assertIn(self.contract, self._contracts_to_invoice())

    def test_disabled_excludes_company_contracts(self):
        self.company.create_recurring_invoices = False
        self.assertNotIn(self.contract, self._contracts_to_invoice())

    def test_enabled_empty_domain_selects_contract(self):
        # An explicit empty domain behaves like no domain: nothing is added.
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = "[]"
        self.assertIn(self.contract, self._contracts_to_invoice())

    def test_matching_domain_selects_contract(self):
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = str([("id", "=", self.contract.id)])
        self.assertIn(self.contract, self._contracts_to_invoice())

    def test_non_matching_domain_excludes_contract(self):
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = str([("id", "=", self.contract.id)])
        # A contract of the same company not matching the domain is excluded,
        # while the matching one is still selected.
        self.assertNotIn(self.contract2, self._contracts_to_invoice())
        self.assertIn(self.contract, self._contracts_to_invoice())

    def test_company_clears_domain_when_disabled(self):
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = "[('id', '=', 1)]"
        self.company.create_recurring_invoices = False
        self.assertFalse(self.company.contract_to_invoice_domain)

    def test_company_keeps_domain_when_enabled(self):
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = "[('id', '=', 1)]"
        self.assertEqual(self.company.contract_to_invoice_domain, "[('id', '=', 1)]")

    def test_multi_company_specific_domain_per_company(self):
        self.company.create_recurring_invoices = True
        self.company.contract_to_invoice_domain = str([("id", "=", self.contract.id)])
        self.company2.create_recurring_invoices = True
        self.company2.contract_to_invoice_domain = str(
            [("id", "=", self.contract_company2.id)]
        )
        contracts = self._contracts_to_invoice()
        # Each company's domain only restricts its own contracts.
        self.assertIn(self.contract, contracts)
        self.assertIn(self.contract_company2, contracts)
        self.assertNotIn(self.contract2, contracts)

    def test_multi_company_non_recurring_company_excluded(self):
        self.company.create_recurring_invoices = True
        self.company2.create_recurring_invoices = False
        contracts = self._contracts_to_invoice()
        self.assertIn(self.contract, contracts)
        self.assertNotIn(self.contract_company2, contracts)

    def test_invalid_domain_syntax_raises(self):
        self.company.create_recurring_invoices = True
        with self.assertRaisesRegex(ValidationError, "is not valid"):
            self.company.contract_to_invoice_domain = "[('id', '=', 1)"

    def test_invalid_domain_field_raises(self):
        self.company.create_recurring_invoices = True
        with self.assertRaisesRegex(ValidationError, "is not valid"):
            self.company.contract_to_invoice_domain = "[('no_such_field', '=', 1)]"
