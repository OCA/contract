# Copyright 2026 Cristiano Mafra Junior - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractAnalyticAccount(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Analytic Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account", "plan_id": cls.analytic_plan.id}
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account 2", "plan_id": cls.analytic_plan.id}
        )
        cls.distribution = {str(cls.analytic_account.id): 100.0}
        cls.distribution_2 = {str(cls.analytic_account_2.id): 100.0}
        cls.multi_distribution = {
            str(cls.analytic_account.id): 60.0,
            str(cls.analytic_account_2.id): 40.0,
        }

    def test_set_analytic_distribution_propagates_to_lines(self):
        self.assertTrue(self.contract2.contract_line_ids)
        self.contract2.analytic_distribution = self.distribution
        for line in self.contract2.contract_line_ids:
            self.assertEqual(line.analytic_distribution, self.distribution)

    def test_multi_plan_distribution_propagates_to_lines(self):
        self.contract2.analytic_distribution = self.multi_distribution
        for line in self.contract2.contract_line_ids:
            self.assertEqual(line.analytic_distribution, self.multi_distribution)

    def test_change_analytic_distribution_resyncs_lines(self):
        self.contract2.analytic_distribution = self.distribution
        self.contract2.analytic_distribution = self.distribution_2
        for line in self.contract2.contract_line_ids:
            self.assertEqual(line.analytic_distribution, self.distribution_2)

    def test_new_line_added_after_analytic_distribution_set(self):
        self.contract2.analytic_distribution = self.distribution
        new_line = self.env["contract.line"].create(
            {
                "contract_id": self.contract2.id,
                "product_id": self.product_1.id,
                "name": "New service line",
                "quantity": 1,
                "uom_id": self.product_1.uom_id.id,
                "price_unit": 50,
                "recurring_rule_type": "monthly",
                "recurring_interval": 1,
                "date_start": "2018-02-15",
                "recurring_next_date": "2018-02-22",
            }
        )
        self.assertEqual(new_line.analytic_distribution, self.distribution)

    def test_new_line_with_explicit_distribution_is_not_overridden(self):
        self.contract2.analytic_distribution = self.distribution
        new_line = self.env["contract.line"].create(
            {
                "contract_id": self.contract2.id,
                "product_id": self.product_1.id,
                "name": "New service line",
                "quantity": 1,
                "uom_id": self.product_1.uom_id.id,
                "price_unit": 50,
                "recurring_rule_type": "monthly",
                "recurring_interval": 1,
                "date_start": "2018-02-15",
                "recurring_next_date": "2018-02-22",
                "analytic_distribution": self.distribution_2,
            }
        )
        self.assertEqual(new_line.analytic_distribution, self.distribution_2)
