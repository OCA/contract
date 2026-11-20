# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import uuid
from contextlib import contextmanager
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import Command, exceptions, fields
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon

LOGGER = "odoo.addons.subscription_oca_payment.models.sale_subscription"


class TestSubscriptionOCAPayment(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                allowed_company_ids=cls.company.ids,
            )
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "pricelist for subscription payments test"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test subscription_oca_payment",
                "property_product_pricelist": cls.pricelist.id,
                "email": "demo1@demo.com",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "partner test subscription_oca_payment 2",
                "property_product_pricelist": cls.pricelist.id,
                "email": "demo2@demo.com",
            }
        )
        cls.product = cls._create_product(
            name="subscription product",
            lst_price=30.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
        )
        cls.provider = cls._prepare_provider()
        cls.tmpl_auto = cls.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        cls.sub = cls.create_sub({"template_id": cls.tmpl_auto.id})
        cls.create_sub_line(cls.sub)

    @classmethod
    def create_sub_template(cls, vals):
        code = uuid.uuid4().hex
        default_vals = {
            "name": "Test Template " + code,
            "code": code,
            "product_ids": [Command.set(cls.product.product_tmpl_id.ids)],
        }
        default_vals.update(vals)
        return cls.env["sale.subscription.template"].create(default_vals)

    @classmethod
    def create_sub(cls, vals):
        default_vals = {
            "company_id": cls.company.id,
            "partner_id": cls.partner.id,
            "template_id": cls.tmpl_auto.id,
            "pricelist_id": cls.pricelist.id,
        }
        default_vals.update(vals)
        return cls.env["sale.subscription"].create(default_vals)

    @classmethod
    def create_sub_line(cls, sub):
        return cls.env["sale.subscription.line"].create(
            {
                "company_id": cls.company.id,
                "sale_subscription_id": sub.id,
                "product_id": cls.product.id,
            }
        )

    @classmethod
    def _prepare_provider(cls):
        bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.company.id)],
            limit=1,
        )
        if not bank_journal:
            bank_journal = cls.env["account.journal"].create(
                {
                    "name": "Test Bank",
                    "type": "bank",
                    "code": "TBNKX",
                    "company_id": cls.company.id,
                }
            )
        provider = cls.env["payment.provider"].create(
            {
                "name": "Test Provider",
                "state": "test",
                "journal_id": bank_journal.id,
                "company_id": cls.company.id,
            }
        )
        if not bank_journal.inbound_payment_method_line_ids.filtered(
            lambda line: line.payment_provider_id == provider
        ):
            cls.env["account.payment.method.line"].create(
                {
                    "name": "Test inbound line",
                    "payment_method_id": cls.env.ref(
                        "account.account_payment_method_manual_in"
                    ).id,
                    "payment_provider_id": provider.id,
                    "journal_id": bank_journal.id,
                }
            )
        return provider

    def _create_payment_token(self, partner, provider=None):
        provider = provider or self.provider
        method = self.env["payment.method"].create(
            {
                "name": "Test Method",
                "code": "none",
                "provider_ids": [Command.set(provider.ids)],
                "support_tokenization": True,
            }
        )
        return self.env["payment.token"].create(
            {
                "partner_id": partner.id,
                "provider_id": provider.id,
                "provider_ref": f"tok-{partner.id}-{uuid.uuid4().hex[:6]}",
                "payment_method_id": method.id,
            }
        )

    def _patch_send(self, state):
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx = tx.with_context(payment_safe_write=True)
            if state == "done":
                tx._set_done()
            elif state == "pending":
                tx._set_pending()
            else:
                tx._set_error("declined")

        return patch.object(tx_model, "_send_payment_request", _fake_send)

    def _patch_mail(self):
        move_send = type(self.env["account.move.send"])
        return patch.object(move_send, "_generate_and_send_invoices", return_value=None)

    def _failure_activities(self, sub):
        summary = sub._payment_failure_activity_summary()
        return sub.activity_ids.filtered(lambda a: a.summary == summary)

    @contextmanager
    def _allow_commit(self):
        with (
            patch.object(type(self.sub), "_can_commit", return_value=True),
            patch.object(self.env.cr, "commit") as mock_commit,
        ):
            yield mock_commit

    def _enable_sale_automatic_invoice(self):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("sale.automatic_invoice", True)
        params.set_param("sale.async_emails", False)

    def _safe(self, transaction):
        return transaction.with_context(payment_safe_write=True)

    def _confirmed_then_failed_invoice(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        invoice = self.sub.invoice_ids
        transaction = invoice.transaction_ids
        # As done by providers that cancel the payment of a late failure
        transaction.payment_id.action_cancel()
        self._safe(transaction)._set_error(
            "late failure", extra_allowed_states=("done",)
        )
        transaction._post_process()
        return invoice, transaction

    def _patch_failure_email(self):
        return patch.object(type(self.env["mail.template"]), "send_mail")

    def _enable_failure_email(self):
        self.tmpl_auto.payment_failure_mail_template_id = self.env.ref(
            "subscription_oca_payment.mail_template_payment_failure"
        )

    def _declined_invoice(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("error"), self._patch_mail():
            self.sub.generate_invoice()
        return self.sub.invoice_ids

    def test_payment_reference_falls_back_to_subscription(self):
        sub = self.create_sub({"code": "AUTOPAYREF"})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner)
        invoice = sub.create_invoice()
        self.assertEqual(invoice.state, "draft")
        with self._patch_send("pending"):
            self.assertTrue(sub.create_payment(invoice))
        transaction = invoice.transaction_ids
        self.assertEqual(len(transaction), 1)
        self.assertIn("AUTOPAYREF", transaction.reference)

    def test_payment_send_request_raises(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        invoice = self.sub.create_invoice()
        tx_model = type(self.env["payment.transaction"])

        def _raise(tx):
            raise RuntimeError("network error")

        with (
            patch.object(tx_model, "_send_payment_request", _raise),
            mute_logger(LOGGER),
        ):
            self.assertFalse(self.sub.create_payment(invoice))
        self.assertTrue(self.sub.payment_exception)
        msgs = self.sub.message_ids.filtered(
            lambda m: "could not be sent" in (m.body or "")
        )
        self.assertEqual(len(msgs), 1)

    def test_payment_token_partner_constraint(self):
        token = self._create_payment_token(self.partner_2)
        with self.assertRaises(exceptions.ValidationError):
            self.sub.payment_token_id = token

    def test_onchange_token_keeps_manual_choice(self):
        token = self._create_payment_token(self.partner)
        self._create_payment_token(self.partner)
        sub = self.env["sale.subscription"].new(
            {
                "template_id": self.tmpl_auto.id,
                "partner_id": self.partner.id,
                "payment_token_id": token.id,
                "company_id": self.company.id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_so_subscription_token_handoff(self):
        self.product.product_tmpl_id.subscription_template_id = self.tmpl_auto
        token = self._create_payment_token(self.partner)
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        tx = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "payment_method_id": token.payment_method_id.id,
                "token_id": token.id,
                "operation": "online_token",
                "reference": "SO-TEST-TOKEN",
                "amount": 100.0,
                "currency_id": so.currency_id.id,
                "partner_id": self.partner.id,
                "state": "done",
            }
        )
        so.transaction_ids = [Command.link(tx.id)]
        so.with_context(uid=1).action_confirm()
        subscription = so.subscription_ids
        self.assertEqual(len(subscription), 1)
        self.assertEqual(subscription.payment_token_id, token)

    def test_generate_invoice_auto_payment_success(self):
        self._enable_sale_automatic_invoice()
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        original_next_date = self.sub.recurring_next_date
        with self._patch_send("done"), self._patch_mail() as mock_send:
            self.sub.generate_invoice()
        invoice = self.sub.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, "posted")
        self.assertIn(invoice.payment_state, ("in_payment", "paid"))
        mock_send.assert_called_once()
        self.assertFalse(self.sub.payment_exception)
        self.assertNotEqual(self.sub.recurring_next_date, original_next_date)
        confirmation = self.sub.message_ids.filtered(
            lambda m: "Automatic payment confirmed for invoice" in (m.body or "")
            and invoice.name in (m.body or "")
        )
        self.assertEqual(len(confirmation), 1)
        self.assertFalse(
            self.sub.message_ids.filtered(
                lambda m: "awaiting confirmation" in (m.body or "")
            )
        )

    def test_generate_invoice_auto_payment_no_token(self):
        original_next_date = self.sub.recurring_next_date
        with self._patch_mail() as mock_send:
            self.sub.generate_invoice()
        mock_send.assert_not_called()
        self.assertTrue(self.sub.payment_exception)
        self.assertEqual(len(self.sub.invoice_ids), 1)
        self.assertEqual(self.sub.invoice_ids.state, "draft")
        self.assertEqual(self.sub.recurring_next_date, original_next_date)
        self.assertTrue(self._failure_activities(self.sub))
        self.assertTrue(
            self.sub.message_ids.filtered(
                lambda m: "No payment token found" in (m.body or "")
            )
        )

    def test_generate_invoice_draft_mode_auto_payment_silent(self):
        template = self.create_sub_template(
            {"invoicing_mode": "draft", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("done"), self._patch_mail() as mock_send:
            sub.generate_invoice()
        self.assertEqual(sub.invoice_ids.state, "posted")
        mock_send.assert_not_called()
        self.assertFalse(sub.payment_exception)

    def test_generate_invoice_sale_and_invoice_auto_payment(self):
        template = self.create_sub_template(
            {"invoicing_mode": "sale_and_invoice", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        self.product.invoice_policy = "order"
        self._enable_sale_automatic_invoice()
        sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("done"), self._patch_mail() as mock_send:
            sub.generate_invoice()
        invoice = sub.sale_order_ids.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, "posted")
        mock_send.assert_not_called()
        self.assertFalse(sub.payment_exception)
        confirmation = sub.message_ids.filtered(
            lambda m: "Automatic payment confirmed for invoice" in (m.body or "")
        )
        self.assertEqual(len(confirmation), 1)

    def test_generate_invoice_sale_and_invoice_retry_reuses_draft(self):
        template = self.create_sub_template(
            {"invoicing_mode": "sale_and_invoice", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        self.product.invoice_policy = "order"
        sub.generate_invoice()
        self.assertTrue(sub.payment_exception)
        self.assertEqual(len(sub.sale_order_ids), 1)
        sub.payment_exception = False
        sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("done"), self._patch_mail():
            sub.generate_invoice()
        self.assertEqual(len(sub.sale_order_ids), 1)
        self.assertEqual(sub.sale_order_ids.invoice_ids.state, "posted")

    def test_generate_invoice_without_auto_payment_unchanged(self):
        template = self.create_sub_template({"invoicing_mode": "invoice_send"})
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        with self._patch_mail() as mock_send:
            sub.generate_invoice()
        mock_send.assert_called_once()
        self.assertEqual(sub.invoice_ids.state, "posted")
        self.assertFalse(sub.invoice_ids.transaction_ids)
        self.assertFalse(sub.payment_exception)

    def test_cron_skips_payment_exception(self):
        sub = self.create_sub(
            {
                "date_start": fields.Date.today() - relativedelta(days=10),
                "in_progress": True,
                "payment_exception": True,
            }
        )
        self.create_sub_line(sub)
        sub.recurring_next_date = fields.Date.today() - relativedelta(days=1)
        sub.cron_subscription_management()
        self.assertEqual(len(sub.invoice_ids), 0)

    def test_cron_auto_payment(self):
        sub = self.create_sub(
            {
                "date_start": fields.Date.today() - relativedelta(days=10),
                "in_progress": True,
            }
        )
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner)
        sub.recurring_next_date = fields.Date.today() - relativedelta(days=1)
        with (
            self._patch_send("done"),
            self._patch_mail() as mock_send,
            self._allow_commit() as mock_commit,
        ):
            sub.cron_subscription_management()
        self.assertEqual(sub.invoice_ids.state, "posted")
        self.assertIn(sub.invoice_ids.payment_state, ("in_payment", "paid"))
        mock_send.assert_called_once()
        # The subscription cron may run each subscription in a savepoint
        mock_commit.assert_not_called()

    def test_transaction_cancel_flags_subscription(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        invoice = self.sub.create_invoice()
        with self._patch_send("pending"):
            self.assertTrue(self.sub.create_payment(invoice))
        self.assertFalse(self.sub.payment_exception)
        stage_before = self.sub.stage_id
        next_date_before = self.sub.recurring_next_date
        invoice.transaction_ids._set_canceled()
        invoice.transaction_ids._post_process()
        self.assertTrue(self.sub.payment_exception)
        self.assertEqual(
            self.sub.payment_exception_transaction_id, invoice.transaction_ids
        )
        self.assertTrue(self._failure_activities(self.sub))
        self.assertEqual(self.sub.stage_id, stage_before)
        self.assertEqual(self.sub.recurring_next_date, next_date_before)

    def test_pending_then_confirmed(self):
        self._enable_sale_automatic_invoice()
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        next_date = self.sub.recurring_next_date
        with self._patch_send("pending"), self._patch_mail() as mock_send:
            self.sub.generate_invoice()
            invoice = self.sub.invoice_ids
            self.assertEqual(invoice.state, "draft")
            self.assertEqual(self.sub.recurring_next_date, next_date)
            # No new invoice while the payment is pending
            self.sub.generate_invoice()
            self.assertEqual(self.sub.invoice_ids, invoice)
            mock_send.assert_not_called()
        awaiting = self.sub.message_ids.filtered(
            lambda m: "awaiting confirmation" in (m.body or "")
        )
        self.assertEqual(len(awaiting), 1)
        transaction = invoice.transaction_ids
        self.assertEqual(len(transaction), 1)
        transaction._set_done()
        with self._patch_mail() as mock_send:
            transaction._post_process()
            self.assertEqual(invoice.state, "posted")
            self.assertNotEqual(self.sub.recurring_next_date, next_date)
            confirmation = self.sub.message_ids.filtered(
                lambda m: "Automatic payment confirmed for invoice" in (m.body or "")
            )
            self.assertEqual(len(confirmation), 1)
            self.assertEqual(confirmation.author_id, self.env.ref("base.partner_root"))
            self.assertNotIn("<b>", confirmation.body)
            mock_send.assert_called_once()
            transaction._post_process()
            confirmation = self.sub.message_ids.filtered(
                lambda m: "Automatic payment confirmed for invoice" in (m.body or "")
            )
            self.assertEqual(len(confirmation), 1)
            mock_send.assert_called_once()

    def test_post_process_failure_keeps_charge(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        original_next_date = self.sub.recurring_next_date
        sub_model = type(self.sub)

        def _raise(sub, transaction):
            raise RuntimeError("post-processing error")

        with (
            self._patch_send("done"),
            self._patch_mail(),
            patch.object(sub_model, "_post_process_payment", _raise),
            mute_logger(LOGGER),
        ):
            self.sub.generate_invoice()
        invoice = self.sub.invoice_ids
        self.assertEqual(invoice.transaction_ids.state, "done")
        self.assertFalse(invoice.transaction_ids.is_post_processed)
        self.assertFalse(self.sub.payment_exception)
        # The charge is not repeated while the payment is in progress
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        self.assertEqual(self.sub.invoice_ids, invoice)
        self.assertEqual(len(invoice.transaction_ids), 1)
        # As retried later by the payment post-processing cron
        with self._patch_mail():
            invoice.transaction_ids._post_process()
        self.assertEqual(invoice.state, "posted")
        self.assertNotEqual(self.sub.recurring_next_date, original_next_date)

    def test_paid_invoice_email_failure_does_not_block_payment(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        move_send = type(self.env["account.move.send"])
        with (
            self._patch_send("done"),
            patch.object(
                move_send,
                "_generate_and_send_invoices",
                side_effect=RuntimeError("mail error"),
            ),
            mute_logger(LOGGER),
        ):
            self.sub.generate_invoice()
        invoice = self.sub.invoice_ids
        self.assertEqual(invoice.state, "posted")
        self.assertIn(invoice.payment_state, ("in_payment", "paid"))

    def test_failure_after_pending_retries_same_period(self):
        original_next_date = self.sub.recurring_next_date
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("pending"), self._patch_mail():
            self.sub.generate_invoice()
        invoice = self.sub.invoice_ids
        transaction = invoice.transaction_ids
        self._safe(transaction)._set_error("insufficient funds")
        transaction._post_process()
        self.assertTrue(self.sub.payment_exception)
        self.assertEqual(self.sub.payment_exception_transaction_id, transaction)
        self.assertEqual(self.sub.recurring_next_date, original_next_date)
        self.assertEqual(invoice.state, "draft")
        self.sub.payment_exception = False
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        self.assertEqual(self.sub.invoice_ids, invoice)
        self.assertEqual(invoice.state, "posted")
        self.assertNotEqual(self.sub.recurring_next_date, original_next_date)

    def test_failure_after_confirmation_not_reused_by_next_period(self):
        first_invoice, __ = self._confirmed_then_failed_invoice()
        self.assertTrue(self.sub.payment_exception)
        self.assertEqual(self.sub._get_failed_payment_invoices(), first_invoice)
        self.sub.payment_exception = False
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        second_invoice = self.sub.invoice_ids - first_invoice
        self.assertEqual(len(second_invoice), 1)
        self.assertIn(second_invoice.payment_state, ("in_payment", "paid"))
        self.assertEqual(first_invoice.payment_state, "not_paid")

    def test_retry_payment_charges_failed_invoice(self):
        invoice, __ = self._confirmed_then_failed_invoice()
        next_date = self.sub.recurring_next_date
        with self._patch_send("done"), self._patch_mail():
            self.sub.action_retry_payment()
        self.assertIn(invoice.payment_state, ("in_payment", "paid"))
        self.assertFalse(self.sub.payment_exception)
        self.assertFalse(self._failure_activities(self.sub))
        self.assertEqual(self.sub.recurring_next_date, next_date)

    def test_retry_payment_current_period_moves_date_on(self):
        original_next_date = self.sub.recurring_next_date
        self.sub.generate_invoice()
        self.assertTrue(self.sub.payment_exception)
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("done"), self._patch_mail():
            self.sub.action_retry_payment()
        self.assertEqual(self.sub.invoice_ids.state, "posted")
        self.assertFalse(self.sub.payment_exception)
        self.assertNotEqual(self.sub.recurring_next_date, original_next_date)

    def test_invoice_paid_online_moves_date_on(self):
        original_next_date = self.sub.recurring_next_date
        token = self._create_payment_token(self.partner)
        invoice = self.sub.create_invoice()
        invoice.action_post()
        transaction = (
            self.env["payment.transaction"]
            .sudo()
            .create(
                {
                    "provider_id": self.provider.id,
                    "payment_method_id": token.payment_method_id.id,
                    "operation": "online_direct",
                    "reference": "ONLINE-PAID",
                    "amount": invoice.amount_residual,
                    "currency_id": invoice.currency_id.id,
                    "partner_id": self.partner.id,
                    "invoice_ids": [Command.set(invoice.ids)],
                }
            )
        )
        self._safe(transaction)._set_done()
        transaction._post_process()
        self.assertIn(invoice.payment_state, ("in_payment", "paid"))
        self.sub.generate_invoice()
        self.assertEqual(self.sub.invoice_ids, invoice)
        self.assertNotEqual(self.sub.recurring_next_date, original_next_date)

    def test_create_payment_rejects_other_invoice(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        other_sub = self.create_sub({"partner_id": self.partner_2.id})
        self.create_sub_line(other_sub)
        other_invoice = other_sub.create_invoice()
        with self.assertRaises(exceptions.UserError):
            self.sub.create_payment(other_invoice)
        self.assertFalse(other_invoice.transaction_ids)

    def test_retry_payment_nothing_to_retry(self):
        with self.assertRaises(exceptions.UserError):
            self.sub.action_retry_payment()

    def test_resubmitted_payment_clears_exception(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("pending"), self._patch_mail():
            self.sub.generate_invoice()
        invoice = self.sub.invoice_ids
        transaction = invoice.transaction_ids
        self._safe(transaction)._set_error("failed")
        transaction._post_process()
        self.assertTrue(self.sub.payment_exception)
        self._safe(transaction)._set_pending(extra_allowed_states=("error",))
        self._safe(transaction)._set_done()
        with self._patch_mail():
            transaction._post_process()
        self.assertFalse(self.sub.payment_exception)
        self.assertFalse(self._failure_activities(self.sub))
        self.assertEqual(invoice.state, "posted")

    def test_reversal_not_cleared_by_other_payment(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        transaction = self.sub.invoice_ids.transaction_ids
        transaction._subscription_payment_reversed("chargeback")
        self.assertTrue(self.sub.payment_exception)
        self.assertEqual(self.sub.payment_exception_transaction_id, transaction)
        other_invoice = self.sub.create_invoice()
        with self._patch_send("done"), self._patch_mail():
            self.assertTrue(self.sub.create_payment(other_invoice))
        self.assertTrue(self.sub.payment_exception)

    def test_declined_charge(self):
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        original_next_date = self.sub.recurring_next_date
        with (
            self._patch_send("error"),
            self._patch_mail(),
            self._patch_failure_email() as mock_email,
        ):
            self.sub.generate_invoice()
            # As done later by the payment post-processing cron
            self.sub.invoice_ids.transaction_ids._post_process()
        self.assertTrue(self.sub.payment_exception)
        self.assertEqual(self.sub.invoice_ids.state, "draft")
        self.assertEqual(self.sub.recurring_next_date, original_next_date)
        self.assertEqual(len(self._failure_activities(self.sub)), 1)
        failures = self.sub.message_ids.filtered(
            lambda m: "declined" in (m.body or "")
            or "failed or was cancelled" in (m.body or "")
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("was declined: declined", failures.body)
        # The failure email is disabled by default
        mock_email.assert_not_called()

    def test_clearing_exception_resolves_activity(self):
        self.sub.generate_invoice()
        self.assertTrue(self._failure_activities(self.sub))
        self.sub.payment_exception = False
        self.assertFalse(self._failure_activities(self.sub))
        self.assertFalse(self.sub.payment_exception_transaction_id)

    def test_subscription_token_takes_precedence(self):
        self.partner.subscription_payment_token_id = self._create_payment_token(
            self.partner
        )
        token = self._create_payment_token(self.partner)
        self.sub.payment_token_id = token
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        self.assertEqual(self.sub.invoice_ids.transaction_ids.token_id, token)

    def test_partner_token_constraint(self):
        token = self._create_payment_token(self.partner_2)
        with self.assertRaises(exceptions.ValidationError):
            self.partner.subscription_payment_token_id = token

    def test_onchange_proposes_partner_token(self):
        token = self._create_payment_token(self.partner)
        self._create_payment_token(self.partner)
        self.partner.subscription_payment_token_id = token
        sub = self.env["sale.subscription"].new(
            {
                "template_id": self.tmpl_auto.id,
                "partner_id": self.partner.id,
                "company_id": self.company.id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_failure_email_renders(self):
        self._enable_failure_email()
        invoice = self.sub.create_invoice()
        template = self.tmpl_auto.payment_failure_mail_template_id
        body = template._render_field("body_html", invoice.ids)[invoice.id]
        self.assertIn(self.sub.name, body)

    def test_failure_email_not_sent_for_internal_error(self):
        self._enable_failure_email()
        provider = self._prepare_provider()
        provider.journal_id = False
        self.sub.payment_token_id = self._create_payment_token(self.partner, provider)
        with self._patch_failure_email() as mock_email:
            self.sub.generate_invoice()
        self.assertTrue(self.sub.payment_exception)
        mock_email.assert_not_called()
        self.assertTrue(
            self.sub.message_ids.filtered(
                lambda m: "no payment journal" in (m.body or "")
            )
        )

    def test_retry_cron_disabled_by_default(self):
        invoice = self._declined_invoice()
        self.tmpl_auto.auto_retry_payment_hours = 0
        with self._patch_send("done"), self._patch_mail():
            self.env["sale.subscription"]._cron_retry_failed_payments()
        self.assertEqual(len(invoice.transaction_ids), 1)
        self.assertTrue(self.sub.payment_exception)

    def test_retry_cron_retries_after_interval(self):
        self.tmpl_auto.auto_retry_payment = True
        invoice = self._declined_invoice()
        with self._patch_send("done"), self._patch_mail():
            self.env["sale.subscription"]._cron_retry_failed_payments()
        self.assertEqual(len(invoice.transaction_ids), 1)
        self.tmpl_auto.auto_retry_payment_hours = 0
        with (
            self._patch_send("done"),
            self._patch_mail(),
            self._allow_commit() as mock_commit,
        ):
            self.env["sale.subscription"]._cron_retry_failed_payments()
        self.assertEqual(invoice.state, "posted")
        self.assertFalse(self.sub.payment_exception)
        mock_commit.assert_called_once()

    def test_retry_cron_stops_after_retries(self):
        self.tmpl_auto.write(
            {
                "auto_retry_payment": True,
                "auto_retry_payment_count": 1,
                "auto_retry_payment_hours": 0,
            }
        )
        invoice = self._declined_invoice()
        for __ in range(3):
            with self._patch_send("error"), self._patch_mail():
                self.env["sale.subscription"]._cron_retry_failed_payments()
        self.assertEqual(len(invoice.transaction_ids), 2)
        self.assertTrue(self.sub.payment_exception)

    def test_onchange_token_when_template_set_after_partner(self):
        token = self._create_payment_token(self.partner)
        sub = self.env["sale.subscription"].new(
            {"partner_id": self.partner.id, "company_id": self.company.id}
        )
        sub._onchange_partner_id_payment_token()
        self.assertFalse(sub.payment_token_id)
        sub.template_id = self.tmpl_auto
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_onchange_token_from_parent_company(self):
        company_partner = self.env["res.partner"].create(
            {"name": "Customer company", "is_company": True}
        )
        contact = self.env["res.partner"].create(
            {"name": "Customer contact", "parent_id": company_partner.id}
        )
        token = self._create_payment_token(company_partner)
        sub = self.env["sale.subscription"].new(
            {
                "template_id": self.tmpl_auto.id,
                "partner_id": contact.id,
                "company_id": self.company.id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_archived_token_not_charged(self):
        token = self._create_payment_token(self.partner)
        self.sub.payment_token_id = token
        token.active = False
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        self.assertTrue(self.sub.payment_exception)
        self.assertFalse(self.sub.invoice_ids.transaction_ids)
        self.assertTrue(
            self.sub.message_ids.filtered(
                lambda m: "has been removed" in (m.body or "")
            )
        )

    def test_archived_token_falls_back_to_partner_token(self):
        archived = self._create_payment_token(self.partner)
        self.sub.payment_token_id = archived
        archived.active = False
        token = self._create_payment_token(self.partner)
        self.partner.subscription_payment_token_id = token
        with self._patch_send("done"), self._patch_mail():
            self.sub.generate_invoice()
        self.assertEqual(self.sub.invoice_ids.transaction_ids.token_id, token)
        self.assertEqual(self.sub.invoice_ids.state, "posted")

    def test_onchange_replaces_archived_token(self):
        archived = self._create_payment_token(self.partner)
        token = self._create_payment_token(self.partner)
        archived.active = False
        sub = self.env["sale.subscription"].new(
            {
                "template_id": self.tmpl_auto.id,
                "partner_id": self.partner.id,
                "payment_token_id": archived.id,
                "company_id": self.company.id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_retried_failures_registered_once(self):
        self._enable_failure_email()
        self.tmpl_auto.write(
            {
                "auto_retry_payment": True,
                "auto_retry_payment_count": 2,
                "auto_retry_payment_hours": 0,
            }
        )
        self.sub.payment_token_id = self._create_payment_token(self.partner)
        with self._patch_failure_email() as mock_email:
            with self._patch_send("error"), self._patch_mail():
                self.sub.generate_invoice()
                for __ in range(2):
                    self.env["sale.subscription"]._cron_retry_failed_payments()
            transactions = self.sub.invoice_ids.transaction_ids
            self.assertEqual(len(transactions), 3)
            # As done later by the payment post-processing cron
            transactions._post_process()
        self.assertEqual(mock_email.call_count, 3)
        mock_email.assert_called_with(self.sub.invoice_ids.id)
        failures = self.sub.message_ids.filtered(
            lambda m: "declined" in (m.body or "")
            or "failed or was cancelled" in (m.body or "")
        )
        self.assertEqual(len(failures), 3)
        self.assertEqual(
            self.sub.payment_exception_transaction_id, transactions.sorted("id")[-1]
        )
