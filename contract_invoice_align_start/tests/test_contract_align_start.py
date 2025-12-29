# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestContractAlignStart(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Service", "type": "service"}
        )

    def test_align_start_date(self):
        """Test alignment of start date to the first of the month."""
        # 1. Create contract starting Jan 15, Monthly, Post-paid
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Align Contract",
                "partner_id": self.partner.id,
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2025-01-15",
                "align_billing_cycle": True,
                "recurring_invoicing_type": "post-paid",
                "recurring_invoicing_offset": 0,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": "Service",
                            "quantity": 1,
                            "price_unit": 100,
                            "recurring_interval": 1,
                            "recurring_rule_type": "monthly",
                            "date_start": "2025-01-15",
                            "recurring_invoicing_type": "post-paid",
                            "recurring_invoicing_offset": 0,
                        },
                    )
                ],
            }
        )

        # Verify initial values
        self.assertEqual(contract.date_start, fields.Date.to_date("2025-01-15"))
        self.assertTrue(contract.align_billing_cycle)

        # 2. Compute and verify period end
        # This calls rec.get_next_period_date_end(..., align_billing_cycle=True)
        contract._compute_next_period_date_end()

        # Force offset to 0 (base contract computes default of 1 for post-paid)
        line = contract.contract_line_ids[0]
        line.recurring_invoicing_offset = 0
        contract.recurring_invoicing_offset = 0

        # DEBUG ASSERT
        self.assertEqual(
            contract.next_period_date_end,
            fields.Date.to_date("2025-01-31"),
            f"First period end should be aligned to Jan 31. "
            f"Got {contract.next_period_date_end}",
        )

        # 3. Compute Next Invoice
        contract._compute_recurring_next_date()
        # For post-paid with 0 offset, next invoice = period end = Jan 31.
        self.assertEqual(
            contract.recurring_next_date,
            fields.Date.to_date("2025-01-31"),
            "First invoice date should be Jan 31 (End of alignment period)",
        )

        # 4. Simulate Invoicing
        invoice = contract._recurring_create_invoice()

        # Verify Proration
        # Period: Jan 15 - Jan 31 = 17 days.
        # Month: Jan = 31 days.
        # Expected Qty = 1 * (17/31)
        expected_qty = 17 / 31
        line = invoice.invoice_line_ids[0]

        self.assertAlmostEqual(
            line.quantity,
            expected_qty,
            places=2,
            msg="Invoice line quantity should be prorated for partial month",
        )
        self.assertIn(
            "Prorated", line.name, "Invoice line description should mention proration"
        )

        # 5. Check Next Period
        line = contract.contract_line_ids[0]
        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-01-31"),
            "First period should end on Jan 31",
        )

        # Update contract computed next date
        contract.invalidate_recordset()
        contract._compute_recurring_next_date()

        # Next period starts Feb 1. Monthly -> Feb 1 to Feb 28.
        # Next invoice should be Feb 28 (Post-paid).
        self.assertEqual(
            contract.recurring_next_date,
            fields.Date.to_date("2025-02-28"),
            "Second invoice date should be Feb 28 (End of first full period)",
        )
