# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestContractVariableQtyTimesheet(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test analytic account"}
        )
        cls.contract = cls.env["contract.contract"].create(
            {"name": "Test contract", "partner_id": cls.partner.id}
        )
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        contract_line_vals = {
            "contract_id": cls.contract.id,
            "analytic_account_id": cls.analytic_account.id,
            "product_id": cls.product.id,
            "uom_id": cls.product.uom_id.id,
            "name": "Test line contract",
            "recurring_interval": 1,
            "recurring_rule_type": "monthly",
            "recurring_invoicing_type": "pre-paid",
            "date_start": "2020-01-01",
            "recurring_next_date": "2020-01-01",
            "qty_type": "variable",
            "qty_formula_id": cls.env.ref(
                "contract_variable_qty_timesheet."
                "contract_line_qty_formula_project_timesheet"
            ).id,
        }
        cls.contract_line = cls.env["contract.line"].create(contract_line_vals)
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "analytic_account_id": cls.analytic_account.id}
        )
        cls.task = cls.env["project.task"].create(
            {"project_id": cls.project.id, "name": "Test task"}
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
                "name": "Test {} {}".format(date, unit_amount),
                "date": date,
                "product_id": product and product.id,
                "unit_amount": unit_amount,
            }
        )

    def test_project_timesheet(self):
        self._create_analytic_line(self.project, self.task, "2020-01-01", False, 3)
        self._create_analytic_line(False, False, "2020-01-01", False, 1)
        invoice = self._contract_invoicing(self.contract)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertAlmostEqual(invoice.invoice_line_ids.quantity, 3)

    def test_task_timesheet(self):
        self.contract_line.qty_formula_id = self.env.ref(
            "contract_variable_qty_timesheet."
            "contract_line_qty_formula_task_timesheet"
        ).id
        self._create_analytic_line(self.project, self.task, "2020-01-01", False, 3)
        self._create_analytic_line(self.project, False, "2020-01-01", False, 1)
        invoice = self._contract_invoicing(self.contract)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertAlmostEqual(invoice.invoice_line_ids.quantity, 3)

    def test_same_product(self):
        self.contract_line.qty_formula_id = self.env.ref(
            "contract_variable_qty_timesheet."
            "contract_line_qty_formula_analytic_same_product"
        ).id
        self._create_analytic_line(False, False, "2020-01-01", self.product, 3)
        self._create_analytic_line(self.project, False, "2020-01-01", False, 1)
        invoice = self._contract_invoicing(self.contract)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertAlmostEqual(invoice.invoice_line_ids.quantity, 3)
