# Copyright 2024 Kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestContractHrValidation(TransactionCase):
    """Test validation and edge cases for the contract_hr module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test employees with different types
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

        # Create test partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "partner@test.com",
            }
        )

    def test_contract_with_inactive_employee(self):
        """Test contract creation with inactive employee"""
        # Deactivate employee
        self.freelancer.active = False

        # Contract should still be created (no validation prevents this)
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": self.freelancer.id,
            }
        )

        self.assertEqual(contract.employee_id, self.freelancer)
        self.assertFalse(contract.employee_id.active)

    def test_contract_with_employee_without_email_phone(self):
        """Test contract creation with employee without email/phone"""
        employee_no_contact = self.env["hr.employee"].create(
            {
                "name": "Employee No Contact",
                "employee_type": "freelance",
            }
        )

        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": employee_no_contact.id,
            }
        )

        # Check that related fields are empty
        self.assertEqual(contract.employee_id, employee_no_contact)
        self.assertFalse(contract.employee_work_email)
        self.assertFalse(contract.employee_work_phone)

    def test_contract_with_employee_with_special_characters(self):
        """Test contract creation with employee having special characters in name"""
        employee_special = self.env["hr.employee"].create(
            {
                "name": "José María O'Connor-Smith",
                "work_email": "jose.maria@test.com",
                "work_phone": "+1-234-567-8900",
                "employee_type": "freelance",
            }
        )

        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": employee_special.id,
            }
        )

        # Check that special characters are handled correctly
        self.assertEqual(contract.employee_name, "José María O'Connor-Smith")
        self.assertEqual(contract.employee_work_email, "jose.maria@test.com")
        self.assertEqual(contract.employee_work_phone, "+1-234-567-8900")

    def test_contract_with_employee_with_empty_strings(self):
        """Test contract creation with employee having empty string fields"""
        employee_empty = self.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "work_email": "",
                "work_phone": "",
                "employee_type": "freelance",
            }
        )

        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": employee_empty.id,
            }
        )

        # Check that empty strings are handled correctly
        self.assertEqual(contract.employee_work_email, "")
        self.assertEqual(contract.employee_work_phone, "")

    def test_contract_with_employee_without_department_job(self):
        """Test contract creation with employee without department/job"""
        employee_no_dept = self.env["hr.employee"].create(
            {
                "name": "Employee No Dept",
                "employee_type": "freelance",
            }
        )

        contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "employee_id": employee_no_dept.id,
            }
        )

        # Check that contract is created but department/job are not set
        self.assertEqual(contract.employee_id, employee_no_dept)
        self.assertFalse(contract.department_id)
        self.assertFalse(contract.job_id)
