# Copyright 2024 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestContractInvoiceOffset(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Service", "type": "service"}
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Offset Contract",
                "partner_id": cls.partner.id,
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2025-01-01",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": "Service #START# - #END#",
                            "quantity": 1,
                            "price_unit": 100,
                            "recurring_interval": 1,
                            "recurring_rule_type": "monthly",
                            "date_start": "2025-01-01",
                        },
                    )
                ],
            }
        )

    def test_prepaid_advance_one_month(self):
        """Test Pre-paid + 1 month advance (offset -1 month)."""
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "recurring_invoicing_offset": 0,
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
            }
        )
        self.contract._compute_recurring_next_date()
        self.assertEqual(
            self.contract.recurring_next_date,
            fields.Date.to_date("2024-12-01"),
            "Invoice date should be one month prior to start date",
        )

    def test_postpaid_delayed_one_month(self):
        """Test Post-paid + 1 month delay."""
        self.contract.write(
            {
                "recurring_invoicing_type": "post-paid",
                "recurring_invoicing_offset": 1,
                "invoicing_offset_type": "months",
                "invoicing_offset_value": 1,
            }
        )

        self.contract._compute_recurring_next_date()
        # End date of first period (2025-01-01 monthly) is 2025-01-31.
        # Apply recurring_invoicing_offset first (1 day), then invoicing_offset_value.
        # Next Invoice Date = 2025-01-31 + 1 day + 1 month = 2025-03-01.
        self.assertEqual(
            self.contract.recurring_next_date,
            fields.Date.to_date("2025-03-01"),
            "Invoice date should be 1 day + 1 month after period end",
        )

    def test_days_fallback(self):
        """Test that 'days' works with consistent behavior
        (both recurring_invoicing_offset and invoicing_offset_value)."""
        self.contract.write(
            {
                "recurring_invoicing_type": "post-paid",
                "recurring_invoicing_offset": 1,
                "invoicing_offset_type": "days",
                "invoicing_offset_value": 5,
            }
        )
        self.contract._compute_recurring_next_date()
        self.assertEqual(
            self.contract.recurring_next_date,
            fields.Date.to_date("2025-02-06"),
            "Invoice date should be 6 days after period end "
            "(1 from recurring_invoicing_offset + 5 from invoicing_offset_value)",
        )

    def test_advance_billing_first_invoice(self):
        """Test that the first invoice with advance billing has correct period.

        With offset = -1 months and date_start = 2025-01-01:
        - recurring_next_date = 2024-12-01 (one month before period start)
        - Invoice period should be Jan 1-31 (the first month of the contract)
        - last_date_invoiced should be 2025-01-31 after invoicing
        """
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
            }
        )

        line = self.contract.contract_line_ids[0]
        # recurring_next_date should be computed as 2024-12-01
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2024-12-01"),
        )

        invoice = self.contract._recurring_create_invoice()
        self.assertTrue(invoice, "Invoice should be created")

        self.assertEqual(
            invoice.invoice_date,
            fields.Date.to_date("2024-12-01"),
            "Invoice date should be Dec 1st (trigger date)",
        )

        # First period: Jan 1 - Jan 31 (first month of contract)
        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-01-31"),
            "last_date_invoiced should be end of first period (Jan 31)",
        )

    def test_advance_billing_consecutive_months(self):
        """Regression test: consecutive invoices must not skip months.

        This is the key test for the cumulative shift bug where:
        - 1st invoice: Feb 1-28 (correct)
        - 2nd invoice: Apr 1-30 (WRONG - skipped March)
        - 3rd invoice: Jun 1-30 (WRONG - skipped May)

        The bug was caused by _get_period_to_invoice shifting first_date_invoiced
        forward every cycle, but last_date_invoiced already reflected the shifted
        period from the previous cycle.
        """
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
            }
        )

        line = self.contract.contract_line_ids[0]

        # Simulate go-live state: already invoiced through December
        line.last_date_invoiced = "2024-12-31"

        # Force recurring_next_date for the January cron run
        line.recurring_next_date = "2025-01-01"

        # === 1st invoice (January cron → February period) ===
        invoice1 = self.contract._recurring_create_invoice()
        self.assertTrue(invoice1, "1st invoice should be created")

        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-02-28"),
            "After 1st invoice: last_date_invoiced should be Feb 28",
        )
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-02-01"),
            "After 1st invoice: recurring_next_date should be Feb 1",
        )

        # === 2nd invoice (February cron → March period) ===
        invoice2 = self.contract._recurring_create_invoice()
        self.assertTrue(invoice2, "2nd invoice should be created")

        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-03-31"),
            "After 2nd invoice: last_date_invoiced should be Mar 31 (NOT Apr 30!)",
        )
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-03-01"),
            "After 2nd invoice: recurring_next_date should be Mar 1",
        )

        # === 3rd invoice (March cron → April period) ===
        invoice3 = self.contract._recurring_create_invoice()
        self.assertTrue(invoice3, "3rd invoice should be created")

        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-04-30"),
            "After 3rd invoice: last_date_invoiced should be Apr 30",
        )
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-04-01"),
            "After 3rd invoice: recurring_next_date should be Apr 1",
        )

    def test_advance_billing_invoice_line_period_markers(self):
        """Test that invoice line names show the correct period dates.

        With advance billing, the #START# and #END# markers must reflect
        the shifted period, not the trigger date.
        """
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
            }
        )

        line = self.contract.contract_line_ids[0]
        line.last_date_invoiced = "2024-12-31"
        line.recurring_next_date = "2025-01-01"

        invoice = self.contract._recurring_create_invoice()
        inv_line = invoice.invoice_line_ids.filtered(
            lambda li: li.display_type == "product"
        )

        # The period should be February (shifted), not January (unshifted)
        self.assertIn(
            "02/01/2025",
            inv_line.name,
            "Invoice line name should contain February start date",
        )
        self.assertIn(
            "02/28/2025",
            inv_line.name,
            "Invoice line name should contain February end date",
        )

    def test_advance_billing_quarterly(self):
        """Test advance billing with quarterly interval."""
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
            }
        )

        line = self.contract.contract_line_ids[0]
        line.write(
            {
                "recurring_interval": 3,
                "recurring_rule_type": "monthly",
            }
        )

        # Simulate state: Q4 2024 invoiced, next trigger Jan 1
        line.last_date_invoiced = "2024-12-31"
        line.recurring_next_date = "2025-01-01"

        # 1st invoice: Q1 2025 (Feb 1 - Apr 30)
        invoice1 = self.contract._recurring_create_invoice()
        self.assertTrue(invoice1)
        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-04-30"),
            "Quarterly advance: last_date_invoiced should be Apr 30",
        )

        # 2nd invoice: Q2 2025 (May 1 - Jul 31)
        invoice2 = self.contract._recurring_create_invoice()
        self.assertTrue(invoice2)
        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-07-31"),
            "Quarterly advance: last_date_invoiced should be Jul 31 (not skip)",
        )

    def test_zero_offset_unchanged(self):
        """Test that contracts with zero offset behave exactly like base."""
        # Default offset is 0/days - should work like standard contract
        line = self.contract.contract_line_ids[0]

        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-01-01"),
        )

        invoice = self.contract._recurring_create_invoice()
        self.assertTrue(invoice)

        self.assertEqual(
            line.last_date_invoiced,
            fields.Date.to_date("2025-01-31"),
            "Zero offset: standard Jan period",
        )
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-02-01"),
            "Zero offset: next date is Feb 1",
        )

    def test_positive_offset_delayed(self):
        """Test that positive offset (delayed billing) still works."""
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": 1,
            }
        )

        line = self.contract.contract_line_ids[0]
        # With +1 month offset, trigger date = period_start + 1 month
        # = 2025-01-01 + 1 month = 2025-02-01
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-02-01"),
            "Positive offset: invoice date should be 1 month after period start",
        )

    def test_advance_billing_contract_ended_before_next_period(self):
        """Test that ended contracts don't generate invoices with invalid periods.

        Regression test: when a contract has date_end before the next advance
        billing period start, _get_period_to_invoice must return (False, False,
        False) instead of inverted dates (start > end), which would crash the
        deferred revenue validation.

        Example: contract ends Feb 10, next period would be March 1-31.
        The date_end clamps period_end to Feb 10, giving Mar 1 > Feb 10.
        """
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
                "date_end": "2025-02-10",
            }
        )

        line = self.contract.contract_line_ids[0]
        line.write({"date_end": "2025-02-10"})

        # Simulate: already invoiced Feb, trigger date is Feb 1
        line.last_date_invoiced = "2025-02-28"
        line.recurring_next_date = "2025-02-01"

        # The next period would be March 1-31, but contract ends Feb 10.
        # _get_period_to_invoice should return False tuple.
        dates = line._get_period_to_invoice(
            line.last_date_invoiced, line.recurring_next_date
        )
        self.assertEqual(
            dates,
            (False, False, False),
            "Ended contract should return False dates, not inverted period",
        )

        # Invoicing should produce nothing, not crash
        invoice = self.contract._recurring_create_invoice()
        self.assertFalse(invoice, "No invoice should be created for ended contract")

    def test_advance_billing_contract_ends_at_period_boundary(self):
        """Test contract ending exactly at the current period boundary.

        Contract ends Feb 28, the current invoiced period is Feb 1-28.
        The next period (March) should NOT be invoiced.
        """
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
                "date_end": "2025-02-28",
            }
        )

        line = self.contract.contract_line_ids[0]
        line.write({"date_end": "2025-02-28"})

        # Simulate: Feb period invoiced, next trigger is Feb 1
        line.last_date_invoiced = "2025-02-28"
        line.recurring_next_date = "2025-02-01"

        # Next period would be Mar 1-31, but contract ends Feb 28
        dates = line._get_period_to_invoice(
            line.last_date_invoiced, line.recurring_next_date
        )
        self.assertEqual(
            dates,
            (False, False, False),
            "Contract ending at period boundary should not generate next period",
        )

    def test_advance_billing_contract_end_within_period(self):
        """Test contract ending mid-period still invoices the partial period.

        Contract ends Feb 15. When invoicing the Feb period (Feb 1-28),
        date_end should clamp it to Feb 1-15 (partial period), which is valid.
        """
        self.contract.write(
            {
                "recurring_invoicing_type": "pre-paid",
                "invoicing_offset_type": "months",
                "invoicing_offset_value": -1,
                "date_end": "2025-02-15",
            }
        )

        line = self.contract.contract_line_ids[0]
        line.write({"date_end": "2025-02-15"})

        # Simulate: Jan period invoiced, trigger Jan 1
        line.last_date_invoiced = "2025-01-31"
        line.recurring_next_date = "2025-01-01"

        # Period should be Feb 1 - Feb 15 (clamped by date_end, but still valid)
        dates = line._get_period_to_invoice(
            line.last_date_invoiced, line.recurring_next_date
        )
        self.assertEqual(
            dates[0],
            fields.Date.to_date("2025-02-01"),
            "Partial period start should be Feb 1",
        )
        self.assertEqual(
            dates[1],
            fields.Date.to_date("2025-02-15"),
            "Partial period end should be clamped to date_end (Feb 15)",
        )
