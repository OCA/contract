# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractInvoiceCompanyDomain(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.contract.company_id

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

    def test_settings_clears_domain_when_disabled(self):
        settings = self.env["res.config.settings"].new(
            {
                "create_recurring_invoices": False,
                "contract_to_invoice_domain": "[('id', '=', 1)]",
            }
        )
        settings._onchange_create_recurring_invoices()
        self.assertFalse(settings.contract_to_invoice_domain)

    def test_settings_keeps_domain_when_enabled(self):
        settings = self.env["res.config.settings"].new(
            {
                "create_recurring_invoices": True,
                "contract_to_invoice_domain": "[('id', '=', 1)]",
            }
        )
        settings._onchange_create_recurring_invoices()
        self.assertEqual(settings.contract_to_invoice_domain, "[('id', '=', 1)]")
