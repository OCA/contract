# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    """
    These tests verify that prorated invoice amounts are correctly computed
    based on recurrence type, interval, invoicing type (pre-paid/post-paid),
    and combinations of start, next, and end dates.

    Main focuses:
    - Monthly and monthly-last-day recurrences
    - Pre-paid and post-paid contracts
    - Edge cases like partial months, contract terminations, or prorations over
    irregular dates
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_1")
        cls.contract = cls.env["contract.contract"].create(
            [
                {
                    "name": "Test Contract 2",
                    "partner_id": cls.partner.id,
                    "pricelist_id": cls.partner.property_product_pricelist.id,
                    "contract_type": "purchase",
                    "contract_line_ids": [
                        Command.create(
                            {
                                "product_id": cls.product.id,
                                "name": "Services from #START# to #END#",
                                "quantity": 1,
                                "uom_id": cls.product.uom_id.id,
                                "price_unit": 100,
                                "discount": 50,
                                "recurring_rule_type": "monthly",
                                "recurring_interval": 1,
                                "date_start": "2016-02-15",
                                "recurring_next_date": "2016-02-29",
                            },
                        )
                    ],
                }
            ]
        )
        cls.contract_line = cls.contract.contract_line_ids[0]

    def _prepare_contract_line(
        self,
        recurring_rule_type,
        recurring_interval,
        recurring_invoicing_type,
        date_start,
        recurring_next_date,
        date_end,
        last_date_invoiced=False,
    ):
        """
        Update the existing contract line with the provided configuration.
        """
        self.contract_line.write(
            {
                "recurring_rule_type": recurring_rule_type,
                "recurring_invoicing_type": recurring_invoicing_type,
                "recurring_interval": recurring_interval,
                "date_start": date_start,
                "recurring_next_date": recurring_next_date,
                "date_end": date_end,
                "last_date_invoiced": last_date_invoiced,
            }
        )

    def _assert_prorated(self, expected_result):
        """
        Assert that the computed prorated invoice value matches the expected result
        within 2 decimals.
        """
        dates = self.contract_line._get_period_to_invoice(
            self.contract_line.last_date_invoiced,
            self.contract_line.recurring_next_date,
        )
        self.assertAlmostEqual(
            expected_result,
            self.contract_line.compute_prorated(*dates),
            places=2,
        )

    # ---- Test cases ----

    def test_prorated_case_1(self):
        """Pre-paid full period (same day start and next date)."""
        self._prepare_contract_line(
            "monthly", 1, "pre-paid", "2018-01-05", "2018-01-05", False
        )
        self._assert_prorated(1.00)

    def test_prorated_case_2(self):
        """Pre-paid, monthly recurrence within January (full month)."""
        self._prepare_contract_line(
            "monthly", 1, "pre-paid", "2018-01-05", "2018-02-01", False, "2018-01-31"
        )
        self._assert_prorated(1.00)

    def test_prorated_case_3(self):
        """Pre-paid full month, start from previous year."""
        self._prepare_contract_line(
            "monthly",
            1,
            "pre-paid",
            "2017-01-05",
            "2018-02-01",
            "2018-03-01",
            "2018-01-31",
        )
        self._assert_prorated(1.00)

    def test_prorated_case_4(self):
        """Pre-paid, partial last month before early termination."""
        self._prepare_contract_line(
            "monthly",
            1,
            "pre-paid",
            "2017-01-05",
            "2018-02-01",
            "2018-02-25",
            "2018-01-31",
        )
        self._assert_prorated(0.892)

    def test_prorated_case_5(self):
        """Post-paid, full monthly period."""
        self._prepare_contract_line(
            "monthly", 1, "post-paid", "2018-01-05", "2018-02-05", False
        )
        self._assert_prorated(1.00)

    def test_prorated_case_6(self):
        """Post-paid, partial February period."""
        self._prepare_contract_line(
            "monthly", 1, "post-paid", "2018-01-05", "2018-02-01", False
        )
        self._assert_prorated(0.87)

    def test_prorated_case_7(self):
        """Post-paid, full year to next February."""
        self._prepare_contract_line(
            "monthly",
            1,
            "post-paid",
            "2017-01-05",
            "2018-02-01",
            "2018-03-01",
            "2017-12-31",
        )
        self._assert_prorated(1.00)

    def test_prorated_case_8(self):
        """Post-paid, partial February coverage."""
        self._prepare_contract_line(
            "monthly",
            1,
            "post-paid",
            "2017-01-05",
            "2018-03-01",
            "2018-02-25",
            "2018-01-31",
        )
        self._assert_prorated(0.892)

    def test_prorated_case_9(self):
        """Post-paid, monthlylastday, full month."""
        self._prepare_contract_line(
            "monthlylastday", 1, "post-paid", "2018-01-01", "2018-01-31", "2018-02-25"
        )
        self._assert_prorated(1.00)

    def test_prorated_case_10(self):
        """Post-paid, monthlylastday, partial month after 5th."""
        self._prepare_contract_line(
            "monthlylastday", 1, "post-paid", "2018-01-05", "2018-01-31", "2018-02-25"
        )
        self._assert_prorated(0.87)

    def test_prorated_case_11(self):
        """Post-paid, monthlylastday, February with partial invoicing."""
        self._prepare_contract_line(
            "monthlylastday",
            1,
            "post-paid",
            "2018-01-05",
            "2018-02-28",
            "2018-02-25",
            "2018-01-31",
        )
        self._assert_prorated(0.892)

    def test_prorated_case_12(self):
        """Post-paid, February month split exactly in half."""
        self._prepare_contract_line(
            "monthlylastday", 1, "post-paid", "2018-02-01", "2018-02-28", "2018-02-14"
        )
        self._assert_prorated(0.5)

    def test_prorated_case_13(self):
        """Post-paid, second half of February only."""
        self._prepare_contract_line(
            "monthlylastday", 1, "post-paid", "2018-02-15", "2018-02-28", False
        )
        self._assert_prorated(0.5)

    def test_prorated_case_14(self):
        """Post-paid, very small fraction for one day in January."""
        self._prepare_contract_line(
            "monthlylastday",
            1,
            "post-paid",
            "2017-02-15",
            "2018-01-31",
            False,
            "2018-01-30",
        )
        self._assert_prorated(0.032)

    def test_prorated_case_15(self):
        """Post-paid, over month boundary with slight overrun."""
        self._prepare_contract_line(
            "monthlylastday",
            1,
            "post-paid",
            "2017-02-15",
            "2018-02-28",
            False,
            "2018-01-30",
        )
        self._assert_prorated(1.035)

    def test_prorated_case_16(self):
        """Post-paid, non-month-end recurrence, tiny fraction."""
        self._prepare_contract_line(
            "monthly", 1, "post-paid", "2017-02-15", "2018-02-01", False, "2018-01-30"
        )
        self._assert_prorated(0.032)

    def test_prorated_case_17(self):
        """Post-paid, larger prorate because of two months in span."""
        self._prepare_contract_line(
            "monthly", 1, "post-paid", "2017-02-15", "2018-03-01", False, "2018-01-30"
        )
        self._assert_prorated(1.035)

    def test_prorated_case_18(self):
        """Pre-paid, clean full month invoicing."""
        self._prepare_contract_line(
            "monthly", 1, "pre-paid", "2017-02-15", "2018-01-01", False, "2017-12-31"
        )
        self._assert_prorated(1.0)

    def test_prorated_case_19(self):
        """Pre-paid, slight overrun from year-end to February."""
        self._prepare_contract_line(
            "monthly", 1, "pre-paid", "2017-02-15", "2018-02-01", False, "2018-01-30"
        )
        self._assert_prorated(1.035)

    def test_prorated_case_20(self):
        """Pre-paid, monthlylastday spanning mid-March."""
        self._prepare_contract_line(
            "monthlylastday", 1, "pre-paid", "2018-03-15", "2018-04-30", False
        )
        self._assert_prorated(1.566)

    def test_prorated_case_21(self):
        """Post-paid, large prorate end of March to April."""
        self._prepare_contract_line(
            "monthly", 1, "post-paid", "2018-03-15", "2018-04-30", False
        )
        self._assert_prorated(1.48)

    def test_prorated_case_22(self):
        """Pre-paid, large prorate mid-March to April."""
        self._prepare_contract_line(
            "monthly", 1, "pre-paid", "2018-03-15", "2018-04-30", False
        )
        self._assert_prorated(2.53)

    def test_prorated_case_23(self):
        """Pre-paid, monthlylastday, full month starting from March 1."""
        self._prepare_contract_line(
            "monthlylastday", 1, "pre-paid", "2018-03-01", "2018-03-01", False
        )
        self._assert_prorated(1.0)

    def test_prorated_case_24(self):
        """Pre-paid, monthlylastday, half-month mid-April start."""
        self._prepare_contract_line(
            "monthlylastday", 1, "pre-paid", "2018-04-16", "2018-04-16", False
        )
        self._assert_prorated(0.5)
