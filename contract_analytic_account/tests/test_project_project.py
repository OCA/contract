# Copyright 2026 Cristiano Mafra Junior - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestProjectProject(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Project Analytic Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Project Analytic Account", "plan_id": cls.analytic_plan.id}
        )
        cls.project = cls.env["project.project"].create(
            {"name": "Test Project", "analytic_account_id": cls.analytic_account.id}
        )
        cls.contract.analytic_distribution = {str(cls.analytic_account.id): 100.0}

    def test_project_contract_count(self):
        self.assertEqual(self.project.contract_count, 1)

    def test_project_without_analytic_account_has_no_contracts(self):
        project = self.env["project.project"].create({"name": "No Analytic Project"})
        self.assertEqual(project.contract_count, 0)

    def test_action_open_project_contracts(self):
        action = self.project.action_open_project_contracts()
        self.assertEqual(action["res_model"], "contract.contract")
        self.assertEqual(action["res_id"], self.contract.id)

    def test_purchase_contract_not_counted(self):
        self.contract2.analytic_distribution = {str(self.analytic_account.id): 100.0}
        self.assertEqual(self.project.contract_count, 1)

    def test_terminated_contract_not_counted(self):
        self.contract.write({"is_terminated": True})
        self.contract.flush_recordset()
        self.project.invalidate_recordset(["contract_count"])
        self.assertEqual(self.project.contract_count, 0)
