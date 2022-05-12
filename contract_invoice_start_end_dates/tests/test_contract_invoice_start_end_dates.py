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
        self.assertTrue(invoice.invoice_line_ids.start_date)
        self.assertTrue(invoice.invoice_line_ids.end_date)
