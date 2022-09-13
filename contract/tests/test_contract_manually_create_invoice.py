# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError
from odoo.tests import tagged

from .test_contract import TestContractBase


@tagged("post_install", "-at_install")
class TestContractManuallyCreateInvoice(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.acct_line.date_start = "2018-01-01"
        cls.acct_line.recurring_invoicing_type = "post-paid"
        cls.acct_line.date_end = "2018-03-15"
        cls.contract2.unlink()

    def test_contract_manually_create_invoice(self):

        contracts = self.contract
        for _i in range(10):
            contracts |= self.contract.copy()
        wizard = self.env["contract.manually.create.invoice"].create(
            {"invoice_date": self.today}
        )
        wizard.action_show_contract_to_invoice()
        contract_to_invoice_count = wizard.contract_to_invoice_count
        self.assertFalse(
            contracts
            - self.env["contract.contract"].search(
                wizard.action_show_contract_to_invoice()["domain"]
            ),
        )
        action = wizard.create_invoice()
        invoice_lines = self.env["account.move.line"].search(
            [("contract_line_id", "in", contracts.mapped("contract_line_ids").ids)]
        )
        self.assertEqual(
            len(contracts.mapped("contract_line_ids")),
            len(invoice_lines),
        )
        invoices = self.env["account.move"].search(action["domain"])
        self.assertFalse(invoice_lines.mapped("move_id") - invoices)
        self.assertEqual(len(invoices), contract_to_invoice_count)

    def test_contract_manually_create_invoice_with_usererror(self):

        contracts = self.contract

        accounts = self.product_1.product_tmpl_id.get_product_accounts()
        accounts["income"].deprecated = True  # To trigger a UserError

        for _i in range(3):
            contracts |= self.contract.copy()
        wizard = self.env["contract.manually.create.invoice"].create(
            {"invoice_date": self.acct_line.date_end}
        )

        with self.assertRaises(UserError):
            # The UserError re-raise a UserError
            wizard.create_invoice()

        try:
            wizard.create_invoice()
        except Exception as e:
            # The re-raised UserError message is the modified one.
            self.assertTrue(str(e).startswith("Failed to process the contract"))
