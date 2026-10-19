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

    def _line_vals(self, **overrides):
        vals = {
            "product_id": self.product.id,
            "name": "Service",
            "quantity": 1,
            "price_unit": 100,
            "recurring_interval": 1,
            "recurring_rule_type": "monthly",
            "date_start": "2025-01-15",
            "recurring_invoicing_type": "post-paid",
        }
        vals.update(overrides)
        return vals

    def _create_contract(self, with_line=True, line_vals=None, **overrides):
        vals = {
            "name": "Test Align Contract",
            "partner_id": self.partner.id,
            "recurring_interval": 1,
            "recurring_rule_type": "monthly",
            "date_start": "2025-01-15",
            "align_billing_cycle": True,
            "recurring_invoicing_type": "post-paid",
        }
        vals.update(overrides)
        if with_line:
            vals["contract_line_ids"] = [(0, 0, self._line_vals(**(line_vals or {})))]
        return self.env["contract.contract"].create(vals)

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

    def test_aligned_period_end_clamped_by_date_end(self):
        """The aligned period never runs past the end of the contract line."""
        contract = self._create_contract(line_vals={"date_end": "2025-01-20"})
        line = contract.contract_line_ids[0]
        self.assertEqual(
            line.next_period_date_end,
            fields.Date.to_date("2025-01-20"),
            "The aligned period end must be clamped to the line end date",
        )

    def test_prepaid_aligned_invoice_date(self):
        """A pre-paid contract is invoiced on the day the period starts."""
        contract = self._create_contract(
            recurring_invoicing_type="pre-paid",
            line_vals={"recurring_invoicing_type": "pre-paid"},
        )
        line = contract.contract_line_ids[0]
        self.assertEqual(
            line.recurring_next_date,
            fields.Date.to_date("2025-01-15"),
        )

    def test_contract_without_lines(self):
        """A contract without lines computes its own aligned invoice date."""
        contract = self._create_contract(with_line=False)
        # The aligned first period ends on Jan 31st, post-paid invoices the
        # day after the period end.
        self.assertEqual(
            contract.recurring_next_date,
            fields.Date.to_date("2025-02-01"),
        )

    def test_no_period_gives_no_invoice_date(self):
        """No period to invoice means no next invoice date."""
        self.assertFalse(
            self.env["contract.contract"].get_next_invoice_date(
                False,
                "post-paid",
                0,
                "monthly",
                1,
                max_date_end=False,
                align_billing_cycle=True,
            )
        )

    def test_period_to_invoice_without_next_date(self):
        """No next invoice date means there is no period to invoice."""
        contract = self._create_contract()
        line = contract.contract_line_ids[0]
        self.assertEqual(
            line._get_period_to_invoice(False, False), (False, False, False)
        )

    def test_compute_prorated_full_month(self):
        """A full calendar month is never prorated, whatever its length."""
        contract = self._create_contract()
        line = contract.contract_line_ids[0]
        self.assertEqual(
            line.compute_prorated(
                fields.Date.to_date("2025-02-01"),
                fields.Date.to_date("2025-02-28"),
                fields.Date.to_date("2025-02-28"),
            ),
            1.0,
            "February must not be prorated down to 28/31",
        )

    def test_compute_prorated_partial_month(self):
        """A partial month falls back to the base day based calculation."""
        contract = self._create_contract()
        line = contract.contract_line_ids[0]
        self.assertAlmostEqual(
            line.compute_prorated(
                fields.Date.to_date("2025-01-15"),
                fields.Date.to_date("2025-01-31"),
                fields.Date.to_date("2025-01-31"),
            ),
            17 / 31,
            places=4,
        )

    def test_compute_prorated_non_monthly(self):
        """Non monthly recurrences fall back to the base calculation."""
        contract = self._create_contract(
            recurring_rule_type="yearly",
            line_vals={"recurring_rule_type": "yearly", "date_start": "2025-01-01"},
        )
        line = contract.contract_line_ids[0]
        self.assertAlmostEqual(
            line.compute_prorated(
                fields.Date.to_date("2025-01-01"),
                fields.Date.to_date("2025-12-31"),
                fields.Date.to_date("2025-12-31"),
            ),
            1.0,
            places=4,
        )

    def test_compute_prorated_without_period(self):
        """Without a period there is nothing to prorate."""
        contract = self._create_contract()
        line = contract.contract_line_ids[0]
        self.assertEqual(
            line.compute_prorated(False, False, fields.Date.to_date("2025-01-31")),
            1.0,
        )

    def test_nullified_line_is_left_alone(self):
        """A line nullified upstream is returned untouched, not prorated."""
        formula = self.env["contract.line.qty.formula"].create(
            {"name": "Nothing to invoice", "code": "result = 0"}
        )
        contract = self._create_contract(
            skip_zero_qty=True,
            line_vals={"qty_type": "variable", "qty_formula_id": formula.id},
        )
        line = contract.contract_line_ids[0]
        self.assertFalse(line._prepare_invoice_line())

    def test_full_month_invoice_is_not_prorated(self):
        """Once aligned, the following full months are billed in full."""
        contract = self._create_contract()
        line = contract.contract_line_ids[0]

        # First invoice: the partial Jan 15th - Jan 31st alignment period.
        contract._recurring_create_invoice()
        self.assertEqual(line.last_date_invoiced, fields.Date.to_date("2025-01-31"))

        # Second invoice: the full month of February.
        invoice = contract._recurring_create_invoice()
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda li: li.display_type == "product"
        )
        self.assertEqual(line.last_date_invoiced, fields.Date.to_date("2025-02-28"))
        self.assertAlmostEqual(invoice_line.quantity, 1.0, places=4)
        self.assertNotIn("Prorated", invoice_line.name)

    def test_non_aligned_contract_is_not_prorated(self):
        """Without the alignment flag the base quantity is left untouched."""
        contract = self._create_contract(align_billing_cycle=False)
        line = contract.contract_line_ids[0]
        vals = line._prepare_invoice_line()
        self.assertAlmostEqual(vals["quantity"], 1.0, places=4)
        self.assertNotIn("Prorated", vals["name"])

    def test_multi_month_period_is_not_prorated(self):
        """A period longer than a month is not a partial month."""
        contract = self._create_contract(
            recurring_interval=2,
            line_vals={"recurring_interval": 2, "date_start": "2025-01-01"},
        )
        line = contract.contract_line_ids[0]
        # Jan 1st - Feb 28th: not a single calendar month, but longer than one.
        self.assertEqual(
            line._get_period_to_invoice(False, line.recurring_next_date)[1],
            fields.Date.to_date("2025-02-28"),
        )
        vals = line._prepare_invoice_line()
        self.assertAlmostEqual(vals["quantity"], 1.0, places=4)
        self.assertNotIn("Prorated", vals["name"])
