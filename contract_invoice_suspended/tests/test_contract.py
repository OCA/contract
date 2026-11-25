# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Contract = cls.env["contract.contract"]
        cls.SuspensionReason = cls.env["contract.automatic.invoice.suspension.reason"]

        # Create test data
        cls.reason = cls.SuspensionReason.create(
            {
                "name": "Test Reason",
                "can_be_selected": True,
            }
        )

        cls.contract = cls.Contract.create(
            {
                "name": "Test Contract",
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "contract_type": "sale",
            }
        )

    def test_suspend_invoicing(self):
        today = fields.Date.today()
        self.contract.is_auto_invoice_suspended = True
        self.contract.auto_invoice_suspended_reason_id = self.reason

        self.assertTrue(self.contract.is_auto_invoice_suspended)
        self.assertEqual(self.contract.auto_invoice_suspended_user_id, self.env.user)
        self.assertEqual(self.contract.auto_invoice_suspended_date, today)
        self.assertEqual(
            self.contract.suspended_reason_category_id,
            self.reason.suspended_reason_category_id,
        )

    def test_resume_invoicing(self):
        self.contract.is_auto_invoice_suspended = True
        self.contract.is_auto_invoice_suspended = False

        self.assertFalse(self.contract.is_auto_invoice_suspended)
        self.assertFalse(self.contract.auto_invoice_suspended_user_id)
        self.assertFalse(self.contract.auto_invoice_suspended_date)
        self.assertFalse(self.contract.auto_invoice_suspended_reason_id)

    def test_contracts_to_invoice_domain(self):
        domain = self.Contract._get_contracts_to_invoice_domain()
        self.assertIn(("is_auto_invoice_suspended", "=", False), domain)

    def test_reason_visibility(self):
        non_selectable_reason = self.SuspensionReason.create(
            {
                "name": "Non-selectable",
                "can_be_selected": False,
            }
        )

        self.contract.write(
            {
                "auto_invoice_suspended_reason_id": non_selectable_reason.id,
            }
        )

        self.assertEqual(
            self.contract.auto_invoice_suspended_reason_id,
            non_selectable_reason,
            "Should allow setting non-selectable reason at ORM level",
        )
