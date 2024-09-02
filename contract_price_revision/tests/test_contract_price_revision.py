# Copyright 2019 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2020 ACSONE SA/NV
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractPriceRevision(TestContractBase):
    def _create_wizard(self, v_type="percentage", value=0.0):
        # TODO: Limitation here, start date should be on the
        # beginning of next period (should not have a gap)
        self.wizard = self.env["contract.price.revision.wizard"].create(
            {
                "date_start": "2018-02-01",
                "variation_type": v_type,
                "variation_percent": value,
                "fixed_price": value,
            }
        )

    def execute_wizard(self):
        self.wizard.with_context(active_ids=self.contract.id).action_apply()

    def test_contract_price_revision_wizard(self):
        # This is for checking if this line is not versioned
        self.acct_line.copy({"automatic_price": True})
        self.assertEqual(len(self.contract.contract_line_ids.ids), 2)
        self._create_wizard(value=100.0)
        self.execute_wizard()
        self.assertEqual(len(self.contract.contract_line_ids.ids), 3)
        lines = self.contract.contract_line_ids.filtered(
            lambda x: x.price_unit == 200.0
        )
        self.assertEqual(len(lines), 1)

    def test_contract_price_fixed_revision_wizard(self):
        # This is for checking if this line is not versioned
        self.acct_line.copy({"automatic_price": True})
        self.assertEqual(len(self.contract.contract_line_ids.ids), 2)
        self._create_wizard(v_type="fixed", value=120.0)
        self.execute_wizard()
        self.assertEqual(len(self.contract.contract_line_ids.ids), 3)
        lines = self.contract.contract_line_ids.filtered(
            lambda x: x.price_unit == 120.0
        )
        self.assertEqual(len(lines), 1)

    def test_contract_price_fixed_revision_wizard_never(self):
        self.acct_line.copy({"never_revise_price": True})
        self.assertEqual(len(self.contract.contract_line_ids.ids), 2)
        self._create_wizard(v_type="fixed", value=120.0)
        self.execute_wizard()
        self.assertEqual(len(self.contract.contract_line_ids.ids), 3)
        lines = self.contract.contract_line_ids.filtered(
            lambda x: x.price_unit == 120.0
        )
        self.assertEqual(len(lines), 1)

    def test_contract_price_revision_invoicing(self):
        self.acct_line.copy({"automatic_price": True})
        self._create_wizard(value=100.0)
        self.execute_wizard()
        invoice = self.contract.recurring_create_invoice()
        invoices = self.env["account.move"].search(
            [
                (
                    "invoice_line_ids.contract_line_id",
                    "in",
                    self.contract.contract_line_ids.ids,
                )
            ]
        )
        self.assertEqual(len(invoices), 1)
        lines = invoice.invoice_line_ids
        self.assertEqual(len(lines), 2)
        lines = lines.filtered(lambda x: x.price_unit == 100.0)
        self.assertEqual(len(lines), 1)
        invoice = self.contract.recurring_create_invoice()
        lines = invoice.invoice_line_ids
        self.assertEqual(len(lines), 2)
        lines = lines.filtered(lambda x: x.price_unit == 200.0)
        self.assertEqual(len(lines), 1)
