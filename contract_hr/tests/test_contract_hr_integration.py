# Copyright 2024 Kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestContractHrIntegration(TransactionCase):
    """Test integration aspects of the contract_hr module with other modules"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test employees
        cls.freelancer = cls.env["hr.employee"].create(
            {
                "name": "Test Freelancer",
                "work_email": "freelancer@test.com",
                "work_phone": "+1234567890",
                "employee_type": "freelance",
            }
        )

        cls.contractor = cls.env["hr.employee"].create(
            {
                "name": "Test Contractor",
                "work_email": "contractor@test.com",
                "work_phone": "+1234567891",
                "employee_type": "contractor",
            }
        )

        # Create test department
        cls.department = cls.env["hr.department"].create(
            {
                "name": "Test Department",
            }
        )

        # Create test job
        cls.job = cls.env["hr.job"].create(
            {
                "name": "Test Job Position",
            }
        )

        # Update employees with department and job
        cls.freelancer.write(
            {
                "department_id": cls.department.id,
                "job_id": cls.job.id,
            }
        )
        cls.contractor.write(
            {
                "department_id": cls.department.id,
                "job_id": cls.job.id,
            }
        )

        # Create test partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "partner@test.com",
            }
        )

    def test_contract_with_hr_contract_integration(self):
        """Test integration with hr_contract module"""
        # Create a contract with employee
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Freelancer Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
            }
        )

        # Check that the contract has the employee information
        self.assertEqual(contract.employee_id, self.freelancer)
        self.assertEqual(contract.employee_type, "freelance")
        self.assertEqual(contract.department_id, self.department)
        self.assertEqual(contract.job_id, self.job)

        # Check that the employee can see the contract
        self.assertIn(contract, self.freelancer.contract_contract_ids)
        self.assertEqual(self.freelancer.contract_contract_count, 1)

    def test_contract_with_multiple_employees_same_partner(self):
        """Test contract creation with multiple employees for the same partner"""
        # Create contracts for different employees with the same partner
        contract1 = self.env["contract.contract"].create(
            {
                "name": "Freelancer Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
            }
        )

        contract2 = self.env["contract.contract"].create(
            {
                "name": "Contractor Contract",
                "partner_id": self.partner.id,
                "employee_id": self.contractor.id,
            }
        )

        # Check that both contracts are created correctly
        self.assertEqual(contract1.partner_id, self.partner)
        self.assertEqual(contract1.employee_id, self.freelancer)
        self.assertEqual(contract2.partner_id, self.partner)
        self.assertEqual(contract2.employee_id, self.contractor)

        # Check that each employee sees only their contracts
        self.assertIn(contract1, self.freelancer.contract_contract_ids)
        self.assertNotIn(contract2, self.freelancer.contract_contract_ids)
        self.assertIn(contract2, self.contractor.contract_contract_ids)
        self.assertNotIn(contract1, self.contractor.contract_contract_ids)

    def test_contract_with_employee_department_job_changes(self):
        """Test contract behavior when employee department/job changes"""
        # Create a contract
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
            }
        )

        # Check initial values
        self.assertEqual(contract.department_id, self.department)
        self.assertEqual(contract.job_id, self.job)

        # Create new department and job
        new_department = self.env["hr.department"].create(
            {
                "name": "New Department",
            }
        )
        new_job = self.env["hr.job"].create(
            {
                "name": "New Job Position",
            }
        )

        # Update employee department and job
        self.freelancer.write(
            {
                "department_id": new_department.id,
                "job_id": new_job.id,
            }
        )

        # Check that contract department and job are not automatically updated
        # (they should remain as they were when the contract was created)
        self.assertEqual(contract.department_id, self.department)
        self.assertEqual(contract.job_id, self.job)

    def test_contract_with_employee_type_change(self):
        """Test contract behavior when employee type changes"""
        # Create a contract
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
            }
        )

        # Check initial employee type
        self.assertEqual(contract.employee_type, "freelance")

        # Change employee type
        self.freelancer.employee_type = "contractor"

        # Check that contract employee type is updated
        contract.refresh()
        self.assertEqual(contract.employee_type, "contractor")

    def test_contract_with_employee_name_change(self):
        """Test contract behavior when employee name changes"""
        # Create a contract
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
            }
        )

        # Check initial employee name
        self.assertEqual(contract.employee_name, "Test Freelancer")

        # Change employee name
        self.freelancer.name = "Updated Freelancer"

        # Check that contract employee name is updated
        contract.refresh()
        self.assertEqual(contract.employee_name, "Updated Freelancer")

    def test_contract_with_different_contract_states(self):
        """Test contracts with different states"""
        # Create contracts with different states
        draft_contract = self.env["contract.contract"].create(
            {
                "name": "Draft Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
                "state": "draft",
            }
        )

        open_contract = self.env["contract.contract"].create(
            {
                "name": "Open Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
                "state": "open",
            }
        )

        close_contract = self.env["contract.contract"].create(
            {
                "name": "Close Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
                "state": "close",
            }
        )

        # Check that all contracts are associated with the employee
        self.freelancer.refresh()
        self.assertEqual(self.freelancer.contract_contract_count, 3)
        self.assertEqual(
            self.freelancer.active_contract_contract_count, 1
        )  # Only open contract

        # Check that only open contract is in active contracts
        self.assertIn(open_contract, self.freelancer.active_contract_contract_ids)
        self.assertNotIn(draft_contract, self.freelancer.active_contract_contract_ids)
        self.assertNotIn(close_contract, self.freelancer.active_contract_contract_ids)
