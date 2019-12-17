# Copyright 2019 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractPriceRevision(TestContractBase):

    def execute_wizard(self):
        wizard = self.env['contract.price.revision.wizard'].create({
            'date_start': '2018-02-15',
            'variation_percent': 100.0,
        })
        wizard.with_context(
            {'active_ids': [self.contract.id]}).action_apply()

    def test_contract_price_revision_wizard(self):
        # This is for checking if this line is not versioned
        self.acct_line.copy({'automatic_price': True})
        self.assertEqual(len(self.contract.contract_line_ids.ids), 2)
        self.execute_wizard()
        self.assertEqual(len(self.contract.contract_line_ids.ids), 3)
        lines = self.contract.contract_line_ids.filtered(
            lambda x: x.price_unit == 200.0)
        self.assertEqual(len(lines), 1)

    def test_contract_price_revision_invoicing(self):
        self.acct_line.copy({'automatic_price': True})
        self.execute_wizard()
        invoice = self.contract.recurring_create_invoice()
        invoices = self.env['account.invoice'].search([
            ('invoice_line_ids.contract_line_id', 'in',
             self.contract.contract_line_ids.ids)])
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
