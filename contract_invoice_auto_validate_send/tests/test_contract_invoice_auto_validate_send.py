# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.addons.contract.tests.test_contract import TestContractBase

TRIGGER = "odoo.addons.base.models.ir_cron.ir_cron._trigger"


class TestContractInvoiceAutoValidateSend(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.contract is a sale contract, so its invoice can be sent.
        cls.contract.company_id.auto_post_contract_invoice = True

    def test_invoice_queued_for_sending_when_enabled(self):
        self.contract.company_id.auto_send_contract_invoice = True
        with mock.patch(TRIGGER) as trigger:
            invoice = self.contract._recurring_create_invoice()
        self.assertEqual(invoice.state, "posted")
        self.assertTrue(
            invoice.sending_data,
            "Invoice should be queued for the async send cron.",
        )
        trigger.assert_called()

    def test_invoice_not_queued_when_disabled(self):
        self.contract.company_id.auto_send_contract_invoice = False
        with mock.patch(TRIGGER) as trigger:
            invoice = self.contract._recurring_create_invoice()
        self.assertEqual(invoice.state, "posted")
        self.assertFalse(invoice.sending_data)
        trigger.assert_not_called()

    def test_purchase_invoice_not_queued(self):
        # Vendor bills (purchase contracts) are never sent to the customer.
        self.contract2.company_id.auto_post_contract_invoice = True
        self.contract2.company_id.auto_send_contract_invoice = True
        with mock.patch(TRIGGER) as trigger:
            invoice = self.contract2._recurring_create_invoice()
        self.assertEqual(invoice.state, "posted")
        self.assertFalse(invoice.sending_data)
        trigger.assert_not_called()

    def test_invoice_not_queued_when_cron_inactive(self):
        self.contract.company_id.auto_send_contract_invoice = True
        self.env.ref("account.ir_cron_account_move_send").active = False
        with (
            mock.patch(TRIGGER) as trigger,
            self.assertLogs(
                "odoo.addons.contract_invoice_auto_validate_send.models."
                "contract_contract",
                level="WARNING",
            ) as log,
        ):
            invoice = self.contract._recurring_create_invoice()
        self.assertEqual(invoice.state, "posted")
        self.assertFalse(invoice.sending_data)
        trigger.assert_not_called()
        self.assertTrue(
            any("not active" in message for message in log.output),
            "A warning should be logged when the send cron is inactive.",
        )

    def test_author_partner_from_company_config(self):
        author = self.env["res.partner"].create({"name": "Invoicing Bot"})
        self.contract.company_id.auto_send_contract_invoice = True
        self.contract.company_id.auto_send_author_partner_id = author
        with mock.patch(TRIGGER):
            invoice = self.contract._recurring_create_invoice()
        self.assertEqual(invoice.sending_data["author_partner_id"], author.id)

    def test_author_partner_defaults_to_company_partner(self):
        company = self.contract.company_id
        company.auto_send_contract_invoice = True
        self.assertEqual(
            company.auto_send_author_partner_id,
            company.partner_id,
            "The author should default to the company's own partner.",
        )
        with mock.patch(TRIGGER):
            invoice = self.contract._recurring_create_invoice()
        self.assertEqual(
            invoice.sending_data["author_partner_id"], company.partner_id.id
        )
