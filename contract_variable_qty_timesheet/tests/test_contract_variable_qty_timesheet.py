# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestContractVariableQtyTimesheet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "company_id": cls.company.id}
        )
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test analytic account",
                "plan_id": cls.plan.id,
                "company_id": cls.company.id,
            }
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test contract",
                "partner_id": cls.partner.id,
                "company_id": cls.company.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "company_id": cls.company.id}
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "company_id": cls.company.id,
            }
        )
        contract_line_vals = {
            "name": "Test contract line",
            "contract_id": cls.contract.id,
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "product_id": cls.product.id,
            "qty_formula_id": cls.env.ref(
                "contract_variable_qty_timesheet.contract_line_qty_formula_project_timesheet"
            ).id,
            "sequence": 10,
            "state": "in-progress",
            "company_id": cls.company.id,
            "qty_type": "variable",
            "analytic_distribution": {str(cls.analytic_account.id): 100},
        }
        cls.contract_line = cls.env["contract.line"].create(contract_line_vals)
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test project",
                "analytic_account_id": cls.analytic_account.id,
                "company_id": cls.company.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "project_id": cls.project.id,
                "name": "Test task",
                "company_id": cls.company.id,
            }
        )

    def _contract_invoicing(self, contract):
        date_ref = fields.Date.from_string("2020-01-01")
        contract._recurring_create_invoice(date_ref)
        return contract._get_related_invoices()

    def _create_analytic_line(self, project, task, date, product, unit_amount):
        return self.env["account.analytic.line"].create(
            {
                "account_id": self.analytic_account.id,
                "project_id": project and project.id,
                "task_id": task and task.id,
                "name": f"Test {date} {unit_amount}",
                "date": date,
                "product_id": product and product.id,
                "unit_amount": unit_amount,
                "employee_id": self.employee.id,
                "company_id": self.company.id,
            }
        )

    def test_project_timesheet(self):
        self._create_analytic_line(self.project, self.task, "2020-01-01", False, 3)
        self._create_analytic_line(False, False, "2020-01-01", False, 1)
        invoice = self.contract._recurring_create_invoice()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertAlmostEqual(invoice.invoice_line_ids.quantity, 3)

    def test_task_timesheet(self):
        self.contract_line.qty_formula_id = self.env.ref(
            "contract_variable_qty_timesheet.contract_line_qty_formula_task_timesheet"
        ).id
        self._create_analytic_line(self.project, self.task, "2020-01-01", False, 3)
        self._create_analytic_line(self.project, False, "2020-01-01", False, 1)
        invoice = self.contract._recurring_create_invoice()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertAlmostEqual(invoice.invoice_line_ids.quantity, 3)

    def test_same_product(self):
        self.contract_line.qty_formula_id = self.env.ref(
            "contract_variable_qty_timesheet.contract_line_qty_formula_analytic_same_product"
        ).id
        self._create_analytic_line(False, False, "2020-01-01", self.product, 3)
        self._create_analytic_line(self.project, False, "2020-01-01", False, 1)
        invoice = self.contract._recurring_create_invoice()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertAlmostEqual(invoice.invoice_line_ids.quantity, 3)
