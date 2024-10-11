# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractAnalyticTag(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Projects Plan",
                "company_id": False,
            }
        )
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {
                "name": "Test account 1",
                "plan_id": cls.plan.id,
            },
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {
                "name": "Test account 2",
                "plan_id": cls.plan.id,
            },
        )
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.analytic_tag_1 = aa_tag_model.create({"name": "Test tag 1"})
        cls.analytic_tag_2 = aa_tag_model.create({"name": "Test tag 2"})

    def test_contract_without_tags(self):
        self.contract2.contract_line_ids.analytic_distribution = {
            self.analytic_account_1.id: 100
        }
        self.contract2.recurring_create_invoice()
        invoice = self.contract2._get_related_invoices()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_contract_with_tag_01(self):
        self.contract2.contract_line_ids.analytic_distribution = {
            self.analytic_account_1.id: 100
        }
        self.contract2.contract_line_ids.analytic_tag_ids = self.analytic_tag_1
        self.contract2.recurring_create_invoice()
        invoice = self.contract2._get_related_invoices()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_contract_with_tag_02(self):
        self.contract2.contract_line_ids.analytic_distribution = {
            self.analytic_account_1.id: 100
        }
        self.contract2.contract_line_ids.analytic_tag_ids = self.analytic_tag_2
        self.contract2.recurring_create_invoice()
        invoice = self.contract2._get_related_invoices()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    def test_contract_with_tags(self):
        self.contract2.contract_line_ids.analytic_distribution = {
            self.analytic_account_1.id: 100
        }
        self.contract2.contract_line_ids.analytic_tag_ids = (
            self.analytic_tag_1 + self.analytic_tag_2
        )
        self.contract2.recurring_create_invoice()
        invoice = self.contract2._get_related_invoices()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)
