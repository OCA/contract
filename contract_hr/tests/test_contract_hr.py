# Copyright 2024 Kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestContractHr(TransactionCase):
    """Test the contract_hr module functionality"""

    def setUp(self):
        super().setUp()
        # Create test employee
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Test Freelancer",
                "work_email": "freelancer@test.com",
                "work_phone": "+1234567890",
                "employee_type": "freelance",
            }
        )

        # Create test department
        self.department = self.env["hr.department"].create(
            {
                "name": "Test Department",
            }
        )

        # Create test job
        self.job = self.env["hr.job"].create(
            {
                "name": "Test Job Position",
            }
        )

        # Update employee with department and job
        self.employee.write(
            {
                "department_id": self.department.id,
                "job_id": self.job.id,
            }
        )

    def test_create_freelancer_contract(self):
        """Test creating a freelancer contract"""
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Freelancer Contract",
                "partner_id": self.env.ref("base.partner_admin").id,
                "employee_id": self.employee.id,
            }
        )

        # Check that the contract was created correctly
        self.assertEqual(contract.employee_id, self.employee)
        self.assertEqual(contract.employee_type, "freelance")
        self.assertEqual(contract.department_id, self.department)
        self.assertEqual(contract.job_id, self.job)
        self.assertEqual(contract.employee_name, "Test Freelancer")
        self.assertEqual(contract.employee_work_email, "freelancer@test.com")
        self.assertEqual(contract.employee_work_phone, "+1234567890")

    def test_employee_contract_relationship(self):
        """Test the relationship between employee and contracts"""
        # Create a freelancer contract
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Freelancer Contract",
                "partner_id": self.env.ref("base.partner_admin").id,
                "is_freelancer": True,
                "employee_id": self.employee.id,
            }
        )

        # Check that the employee can see the contract
        self.assertIn(contract, self.employee.contract_contract_ids)
        self.assertEqual(self.employee.contract_contract_count, 1)

    def test_contract_without_employee(self):
        """Test that regular contracts don't show employee fields"""
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Regular Contract",
                "partner_id": self.env.ref("base.partner_admin").id,
            }
        )

        # Check that employee fields are not set
        self.assertFalse(contract.employee_id)
        self.assertFalse(contract.department_id)
        self.assertFalse(contract.job_id)
        self.assertFalse(contract.employee_type)

    def test_onchange_employee_id(self):
        """Test the onchange method for employee_id"""
        contract = self.env["contract.contract"].new(
            {
                "name": "Test Contract",
                "partner_id": self.env.ref("base.partner_admin").id,
                "is_freelancer": True,
            }
        )

        # Trigger onchange
        contract.employee_id = self.employee

        # Check that department and job are set
        self.assertEqual(contract.department_id, self.department)
        self.assertEqual(contract.job_id, self.job)

    def test_contractor_employee_type(self):
        """Test creating a contract with contractor employee type"""
        contractor = self.env["hr.employee"].create(
            {
                "name": "Test Contractor",
                "work_email": "contractor@test.com",
                "work_phone": "+1234567890",
                "employee_type": "contractor",
            }
        )

        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contractor Contract",
                "partner_id": self.env.ref("base.partner_admin").id,
                "employee_id": contractor.id,
            }
        )

        # Check that the contract was created correctly
        self.assertEqual(contract.employee_id, contractor)
        self.assertEqual(contract.employee_type, "contractor")
        self.assertEqual(contract.employee_name, "Test Contractor")
