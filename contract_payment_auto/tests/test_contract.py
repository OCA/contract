# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import mock
from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from odoo.addons.contract.tests.test_contract import TestContractBase
from odoo.addons.contract_payment_auto.models import contract


@tagged("-at_install", "post_install")
class TestContract(HttpCase, TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a fake model to override PaymentTransaction method
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import TransactionTest

        cls.loader.update_registry((TransactionTest,))

        cls.provider = cls.env["payment.provider"].create(
            {
                "name": "Test Acquirer",
                "inline_form_view_id": cls.env["ir.ui.view"].search([], limit=1).id,
            }
        )
        cls.payment_token = cls.env["payment.token"].create(
            {
                "payment_details": "Test Token",
                "partner_id": cls.partner.id,
                "active": True,
                "provider_id": cls.provider.id,
                "provider_ref": "Test",
            }
        )
        cls.other_payment_token = cls.env["payment.token"].create(
            {
                "payment_details": "Test Other Token",
                "partner_id": cls.partner.id,
                "active": True,
                "provider_id": cls.provider.id,
                "provider_ref": "OtherTest",
            }
        )

        cls.contract.payment_token_id = cls.payment_token

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def _validate_invoice(self, invoice):
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice._name, "account.move")

    def _create_invoice(self, posted=False, sent=False):
        self.contract.is_auto_pay = False
        invoice = self.contract._recurring_create_invoice()
        if posted or sent:
            invoice.action_post()
        if sent:
            invoice.is_move_sent = True
        self.contract.is_auto_pay = True
        return invoice

    def test_onchange_partner_id_payment_token(self):
        """It should clear the payment token."""
        self.assertTrue(self.contract.payment_token_id)
        self.contract._onchange_partner_id_payment_token()
        self.assertFalse(self.contract.payment_token_id)

    def test_create_invoice_no_autopay(self):
        """It should return the new invoice without calling autopay."""
        self.contract.is_auto_pay = False
        with mock.patch.object(contract.Contract, "_do_auto_pay") as method:
            invoice = self.contract._recurring_create_invoice()
            self._validate_invoice(invoice)
            method.assert_not_called()

    def test_create_invoice_autopay(self):
        """It should return the new invoice after calling autopay."""
        self.contract.is_auto_pay = True
        with mock.patch.object(contract.Contract, "_do_auto_pay") as method:
            invoice = self.contract._recurring_create_invoice()
            self._validate_invoice(invoice)
            method.assert_called_once_with(invoice)

    def test_do_auto_pay_ensure_one(self):
        """It should ensure_one on self."""
        with self.assertRaises(ValueError):
            self.env["contract.contract"]._do_auto_pay(
                self._create_invoice(),
            )

    def test_do_auto_pay_invoice_ensure_one(self):
        """It should ensure_one on the invoice."""
        with self.assertRaises(ValueError):
            self.contract._do_auto_pay(
                self.env["account.move"],
            )

    def test_do_auto_pay_open_invoice(self):
        """It should open the invoice."""
        invoice = self._create_invoice()
        self.contract._do_auto_pay(invoice)
        self.assertEqual(invoice.state, "posted")

    def test_do_auto_pay_sends_message(self):
        """It should call the send message method with the invoice."""
        with mock.patch.object(contract.Contract, "_send_invoice_message") as m:
            invoice = self._create_invoice()
            self.contract._do_auto_pay(invoice)
            m.assert_called_once_with(invoice)

    def test_do_auto_pay_does_pay(self):
        """It should try to pay the invoice."""
        with mock.patch.object(contract.Contract, "_pay_invoice") as m:
            invoice = self._create_invoice()
            self.contract._do_auto_pay(invoice)
            m.assert_called_once_with(invoice)

    def test_pay_invoice_not_open(self):
        """It should return None if the invoice isn't open."""
        invoice = self._create_invoice()
        res = self.contract._pay_invoice(invoice)
        self.assertIs(res, None)

    def test_pay_invoice_no_residual(self):
        """It should return None if no residual on the invoice."""
        invoice = self._create_invoice()
        invoice.state = "posted"
        res = self.contract._pay_invoice(invoice)
        self.assertIs(res, None)

    def test_pay_invoice_no_token(self):
        """It should return None if no payment token."""
        self.contract.payment_token_id = False
        invoice = self._create_invoice(True)
        res = self.contract._pay_invoice(invoice)
        self.assertIs(res, None)

    def assert_successful_pay_invoice(self, expected_token=None):
        invoice = self._create_invoice(True)
        res = self.contract.with_context(test_target_state="done")._pay_invoice(invoice)
        self.assertTrue(res)
        if expected_token is not None:
            self.assertEqual(invoice.transaction_ids[0].token_id, expected_token)

    def test_pay_invoice_success(self):
        """It should return True on success."""
        self.assert_successful_pay_invoice()

    def test_pay_invoice_with_contract_token(self):
        """When contract and partner have a token, contract's is used."""
        self.partner.payment_token_id = self.other_payment_token
        self.contract.payment_token_id = self.payment_token
        self.assert_successful_pay_invoice(expected_token=self.payment_token)

    def test_pay_invoice_with_partner_token_success(self):
        """When contract has no related token, it should use partner's."""
        self.contract.payment_token_id = False
        self.partner.payment_token_id = self.other_payment_token
        self.assert_successful_pay_invoice(expected_token=self.other_payment_token)

    @mute_logger(contract.__name__)
    def test_pay_invoice_exception(self):
        """It should catch exceptions."""
        invoice = self._create_invoice(True)
        res = self.contract.with_context(test_target_state="Exception")._pay_invoice(
            invoice
        )
        self.assertIs(res, None)

    def test_pay_invoice_invalid_state(self):
        """It should return None on invalid state."""
        invoice = self._create_invoice(True)
        invoice.state = "draft"
        res = self.contract.with_context(test_target_state="done")._pay_invoice(invoice)
        self.assertIs(res, None)

    @mute_logger(contract.__name__)
    def test_pay_invoice_increments_retries(self):
        """It should increment invoice retries on failure."""
        invoice = self._create_invoice(True)
        self.assertFalse(invoice.auto_pay_attempts)
        self.contract.with_context(test_target_state="draft")._pay_invoice(invoice)
        self.assertTrue(invoice.auto_pay_attempts)

    def test_pay_invoice_updates_fail_date(self):
        """It should update the invoice auto pay fail date on failure."""
        invoice = self._create_invoice(True)
        self.assertFalse(invoice.auto_pay_failed)
        self.contract.with_context(test_target_state="draft")._pay_invoice(invoice)
        self.assertTrue(invoice.auto_pay_failed)

    def test_pay_invoice_too_many_attempts(self):
        """It should clear autopay after too many attempts."""
        invoice = self._create_invoice(True)
        invoice.auto_pay_attempts = self.contract.auto_pay_retries - 1
        self.contract.with_context(test_target_state="draft")._pay_invoice(invoice)
        self.assertFalse(self.contract.is_auto_pay)
        self.assertFalse(self.contract.payment_token_id)

    def test_pay_invoice_too_many_attempts_partner_token(self):
        """It should clear the partner token when attempts were on it."""
        self.partner.payment_token_id = self.contract.payment_token_id
        invoice = self._create_invoice(True)
        invoice.auto_pay_attempts = self.contract.auto_pay_retries
        self.contract.with_context(test_target_state="draft")._pay_invoice(invoice)
        self.assertFalse(self.partner.payment_token_id)

    def test_get_tx_vals(self):
        """It should return a dict."""
        self.assertIsInstance(
            self.contract._get_tx_vals(
                self._create_invoice(), self.contract.payment_token_id
            ),
            dict,
        )

    def test_send_invoice_message_sent(self):
        """It should return None if the invoice has already been sent."""
        invoice = self._create_invoice(sent=True)
        res = self.contract._send_invoice_message(invoice)
        self.assertIs(res, None)

    def test_send_invoice_message_no_template(self):
        """It should return None if the invoice isn't sent."""
        invoice = self._create_invoice(True)
        self.contract.invoice_mail_template_id = False
        res = self.contract._send_invoice_message(invoice)
        self.assertIs(res, None)

    def test_send_invoice_message_sets_invoice_state(self):
        """It should set the invoice to sent."""
        invoice = self._create_invoice(True)
        self.assertFalse(invoice.is_move_sent)
        self.contract._send_invoice_message(invoice)
        self.assertTrue(invoice.is_move_sent)

    def test_send_invoice_message_returns_mail(self):
        """It should create and return the message."""
        invoice = self._create_invoice(True)
        res = self.contract._send_invoice_message(invoice)
        self.assertEqual(res._name, "mail.mail")

    def test_cron_retry_auto_pay_needed(self):
        """It should auto-pay the correct invoice if needed."""
        invoice = self._create_invoice(True)
        invoice.write(
            {
                "auto_pay_attempts": 1,
                "auto_pay_failed": "2015-01-01 00:00:00",
            }
        )
        meth = mock.MagicMock()
        self.contract._patch_method("_do_auto_pay", meth)
        try:
            self.contract.cron_retry_auto_pay()
        finally:
            self.contract._revert_method("_do_auto_pay")
        meth.assert_called_once_with(invoice)

    def test_cron_retry_auto_pay_skip(self):
        """It should skip invoices that don't need to be paid."""
        invoice = self._create_invoice(True)
        invoice.write(
            {
                "auto_pay_attempts": 1,
                "auto_pay_failed": fields.Datetime.now(),
            }
        )
        meth = mock.MagicMock()
        self.contract._patch_method("_do_auto_pay", meth)
        try:
            self.contract.cron_retry_auto_pay()
        finally:
            self.contract._revert_method("_do_auto_pay")
        meth.assert_not_called()
