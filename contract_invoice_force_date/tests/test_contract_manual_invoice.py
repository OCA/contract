# Copyright 2026 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from dateutil.relativedelta import relativedelta

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractInvoicing(TestContractBase):
    """
    Tests for forced date on manual contract invoicing
    """

    def test_contract_manual_invoice_force_date(self):
        tomorrow = self.today + relativedelta(days=1)
        wizard = self.env["contract.manually.create.invoice"].create(
            {"invoice_date": self.today}
        )
        wizard.invoice_date_forced = tomorrow
        action = wizard.create_invoice()
        invoices = self.env["account.move"].search(action["domain"])
        for invoice in invoices:
            self.assertEqual(invoice.invoice_date, tomorrow)
