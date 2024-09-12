# Copyright 2022 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractInvoiceStartEndDates(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract.date_end = "2018-12-31"
        cls.acct_line.product_id.must_have_dates = True

    def test_invoice_start_end_dates(self):
        invoice = self.contract.recurring_create_invoice()
        self.assertTrue(
            invoice.invoice_line_ids.start_date,
            "Start date is not present in invoice line",
        )
        self.assertTrue(
            invoice.invoice_line_ids.end_date,
            "End date is not present in invoice line",
        )

        # Test scenario where product must not have dates
        self.acct_line.product_id.must_have_dates = False
        invoice = self.contract.recurring_create_invoice()
        self.assertFalse(
            invoice.invoice_line_ids.start_date,
            "Start date should not be present in invoice line",
        )
        self.assertFalse(
            invoice.invoice_line_ids.end_date,
            "End date should not be present in invoice line",
        )

        # Test scenario where contract has no end date
        self.contract.date_end = False
        invoice = self.contract.recurring_create_invoice()
        self.assertFalse(
            invoice.invoice_line_ids.start_date,
            "Start date should not be present in invoice line",
        )
        self.assertFalse(
            invoice.invoice_line_ids.end_date,
            "End date should not be present in invoice line",
        )
