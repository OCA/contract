# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo.exceptions import ValidationError

from odoo.addons.contract.tests.test_contract import TestContractBase, to_date


class TestContractRefund(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.acct_line.date_start = "2018-01-01"
        cls.contract.company_id.enable_contract_line_refund_on_stop = True

    def _get_contract_invoices(self):
        return self.env["account.move"].search(
            [("line_ids.contract_line_id", "in", self.contract.contract_line_ids.ids)]
        )

    def test_0(self):
        """
        standard behavior
        stop before last date invoiced, company setting disabled, validationError raises
        """
        self.contract.company_id.enable_contract_line_refund_on_stop = False
        self.contract.recurring_create_invoice()
        with self.assertRaisesRegex(
            ValidationError,
            "You can't have the end date before the date of last invoice",
        ):
            self.acct_line.stop(self.acct_line.last_date_invoiced - timedelta(days=1))

    def test_1(self):
        """
        stop create a refund for the invoiced period
        if the company setting is enabled and the stop is before the last date invoiced
        a refund is created
        """
        self.contract.recurring_create_invoice()
        self.assertEqual(len(self._get_contract_invoices()), 1)
        self.acct_line.stop(self.acct_line.last_date_invoiced - timedelta(days=30))
        self.assertEqual(len(self._get_contract_invoices()), 2)
        refund = self._get_contract_invoices().filtered(
            lambda m: m.move_type == "out_refund"
        )
        self.assertTrue(refund)
        refund_line = refund.invoice_line_ids
        self.assertEqual(refund_line.product_id, self.acct_line.product_id)
        self.assertEqual(refund_line.quantity, 1)
        self.assertEqual(refund_line.name, "Refund for period 01/01/2018 01/31/2018")

    def test_2(self):
        """
        no refund if the stop is after the last date invoiced
        """
        self.contract.recurring_create_invoice()
        self.assertEqual(len(self._get_contract_invoices()), 1)
        self.acct_line.stop(self.acct_line.last_date_invoiced + timedelta(days=1))
        self.assertEqual(len(self._get_contract_invoices()), 1)

    def _test_refund_quantity_prorated(self, stop_date, expected_quantity):
        self.acct_line.stop(stop_date)
        refund = self._get_contract_invoices().filtered(
            lambda m: m.move_type == "out_refund"
        )
        self.assertTrue(refund)
        refund_line = refund.invoice_line_ids
        self.assertEqual(refund_line.quantity, expected_quantity)

    def test_3(self):
        """stop after creating two invoices, refund 2 periods"""
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self._test_refund_quantity_prorated(to_date("2018-01-01"), 2)

    def test_4(self):
        """stop after creating two invoices, refund one period and a half"""
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self._test_refund_quantity_prorated(to_date("2018-01-15"), 1.5)

    def test_5(self):
        """stop after creating two invoices, refund 3 periods"""
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        with self.assertRaisesRegex(
            ValidationError,
            "You can't have the start date after the date of last invoice"
            " for the contract line",
        ):
            self._test_refund_quantity_prorated(to_date("2017-12-01"), 3)

    def test_6(self):
        """monthlylastday post-paid stop after creating two invoices, refund 2
        periods"""
        self.acct_line.recurring_rule_type = "monthlylastday"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-01-31"))
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self._test_refund_quantity_prorated(to_date("2018-01-01"), 2)

    def test_7(self):
        """monthlylastday post-paid stop after creating two invoices, refund 1.5
        periods"""
        self.acct_line.recurring_rule_type = "monthlylastday"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-01-31"))
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self._test_refund_quantity_prorated(to_date("2018-01-16"), 1.52)

    def test_8(self):
        """monthlylastday pre-paid stop after creating two invoices, refund 1.5
        periods"""
        self.acct_line.recurring_rule_type = "monthlylastday"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-01-01"))
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self._test_refund_quantity_prorated(to_date("2018-01-16"), 1.52)

    def test_9(self):
        """yearly pre-paid stop after creating one invoice, refund 0.5 periods"""
        self.acct_line.recurring_rule_type = "yearly"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-01-01"))
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-12-31"))
        self._test_refund_quantity_prorated(to_date("2018-06-30"), 0.51)
