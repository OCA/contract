# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAutoInvoiceSuspensionReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SuspensionReason = cls.env["contract.automatic.invoice.suspension.reason"]
        cls.company1 = cls.env["res.company"].create({"name": "Company 1"})
        cls.company2 = cls.env["res.company"].create({"name": "Company 2"})

        # Create some test reasons
        cls.reason_category = cls.SuspensionReason.create(
            {
                "name": "Maintenance",
                "can_be_selected": False,
            }
        )
        cls.reason_sub1 = cls.SuspensionReason.create(
            {
                "name": "Scheduled Maintenance",
                "parent_id": cls.reason_category.id,
                "can_be_selected": True,
            }
        )
        cls.reason_sub2 = cls.SuspensionReason.create(
            {
                "name": "Emergency Maintenance",
                "parent_id": cls.reason_category.id,
                "can_be_selected": True,
            }
        )

    def test_compute_display_name(self):
        # Test with parent (hierarchical name)
        self.reason_sub1._compute_display_name()
        self.assertEqual(
            self.reason_sub1.display_name,
            f"{self.reason_category.name} - {self.reason_sub1.name}",
            "Display name should include parent name for child records",
        )

        # Test without parent (simple name)
        self.reason_category._compute_display_name()
        self.assertEqual(
            self.reason_category.display_name,
            self.reason_category.name,
            "Display name should be just the name for parent records",
        )

        # Test multiple records at once
        reasons = self.reason_category + self.reason_sub1 + self.reason_sub2
        reasons._compute_display_name()

        self.assertEqual(
            self.reason_category.display_name,
            self.reason_category.name,
            "Parent record display name should remain unchanged",
        )
        self.assertEqual(
            self.reason_sub2.display_name,
            f"{self.reason_category.name} - {self.reason_sub2.name}",
            "Second child record should have correct display name",
        )

    def test_compute_suspended_reason_category_id(self):
        self.assertEqual(
            self.reason_sub1.suspended_reason_category_id, self.reason_category
        )
        self.assertEqual(
            self.reason_category.suspended_reason_category_id, self.reason_category
        )

    def test_check_recursion(self):
        with self.assertRaises(ValidationError):
            self.reason_category.write({"parent_id": self.reason_sub1.id})

    def test_multi_company(self):
        reason = self.SuspensionReason.create(
            {
                "name": "Company Specific",
                "company_id": self.company1.id,
            }
        )

        # Test company1 user can access
        user = self.env["res.users"].create(
            {
                "name": "Company1 User",
                "login": "company1_user",
                "company_id": self.company1.id,
                "company_ids": [(6, 0, [self.company1.id])],
                "groups_id": [
                    (6, 0, [self.env.ref("account.group_account_invoice").id])
                ],
            }
        )
        self.assertTrue(reason.with_user(user).exists())

        # Test company2 user cannot access
        user = self.env["res.users"].create(
            {
                "name": "Company2 User",
                "login": "company2_user",
                "company_id": self.company2.id,
                "company_ids": [(6, 0, [self.company2.id])],
                "groups_id": [
                    (6, 0, [self.env.ref("account.group_account_invoice").id])
                ],
            }
        )
        with self.assertRaises(AccessError):
            reason.with_user(user).read(["name"])
