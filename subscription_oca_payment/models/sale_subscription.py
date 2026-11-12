# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import date, timedelta

from markupsafe import Markup

from odoo import Command, api, fields, models, modules, tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    auto_create_payment = fields.Boolean(related="template_id.auto_create_payment")
    commercial_partner_id = fields.Many2one(related="partner_id.commercial_partner_id")
    payment_token_id = fields.Many2one(
        comodel_name="payment.token",
        domain="[('partner_id', 'child_of', commercial_partner_id)]",
        help="If empty, the customer's subscription payment token is used.",
    )
    payment_exception = fields.Boolean(
        copy=False,
        tracking=True,
        help="Set when an automatic payment fails. Invoicing is skipped "
        "until it is cleared.",
    )
    payment_exception_transaction_id = fields.Many2one(
        comodel_name="payment.transaction",
        string="Failed Payment",
        copy=False,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        subscriptions = super().create(vals_list)
        for subscription in subscriptions.filtered(
            lambda s: s.auto_create_payment
            and s.sale_order_id
            and not s.payment_token_id
        ):
            subscription._assign_payment_token_from_sale_order()
        return subscriptions

    def write(self, vals):
        if "payment_exception" in vals and not vals["payment_exception"]:
            vals = dict(vals, payment_exception_transaction_id=False)
            summary = self._payment_failure_activity_summary()
            self.activity_ids.filtered(lambda a: a.summary == summary).unlink()
        return super().write(vals)

    def _assign_payment_token_from_sale_order(self):
        self.ensure_one()
        token = (
            self.sale_order_id.transaction_ids.filtered(
                lambda tx: tx.state in ("done", "authorized") and tx.token_id
            )
            .sorted("last_state_change", reverse=True)[:1]
            .token_id
        )
        if token:
            self.payment_token_id = token

    @api.onchange("partner_id", "template_id")
    def _onchange_partner_id_payment_token(self):
        for record in self:
            if not record.auto_create_payment or not record.partner_id:
                continue
            if (
                record.payment_token_id.active
                and record.payment_token_id.partner_id.commercial_partner_id
                == record.partner_id.commercial_partner_id
            ):
                continue
            record.payment_token_id = record._get_partner_payment_token() or (
                record.env["payment.token"]
                .sudo()
                .search(
                    [
                        (
                            "partner_id",
                            "child_of",
                            record.partner_id.commercial_partner_id.id,
                        ),
                        ("company_id", "=", record.company_id.id),
                    ],
                    limit=1,
                    order="write_date desc",
                )
            )

    def _get_partner_payment_token(self):
        self.ensure_one()
        partner = self.partner_id
        return (
            partner.subscription_payment_token_id
            or partner.commercial_partner_id.subscription_payment_token_id
        ).filtered("active")

    def _get_payment_token(self):
        """Archived tokens, e.g. removed by the customer, are never charged."""
        self.ensure_one()
        return (
            self.payment_token_id.filtered("active")
            or self._get_partner_payment_token()
        )

    @api.constrains("payment_token_id", "partner_id")
    def _check_payment_token_partner(self):
        for record in self:
            if not record.payment_token_id:
                continue
            if (
                record.payment_token_id.partner_id.commercial_partner_id
                != record.partner_id.commercial_partner_id
            ):
                raise ValidationError(
                    self.env._(
                        "Payment token '%s' belongs to a different partner "
                        "and cannot be used for this subscription.",
                        record.payment_token_id.display_name,
                    )
                )

    def generate_invoice(self):
        if not self.auto_create_payment:
            return super().generate_invoice()
        self.ensure_one()
        if self.payment_exception:
            return
        self._generate_invoice_with_payment()

    def _generate_invoice_with_payment(self):
        """The invoice stays in draft and is only posted once paid. The next
        invoice date is moved on when the payment is confirmed."""
        self.ensure_one()
        invoice = self._get_current_period_invoice()
        # Checked first: an invoice paid outside the automatic payment, e.g.
        # online, also has an accepted transaction
        if invoice.payment_state in ("paid", "in_payment"):
            self._set_next_invoice_date_after_invoice()
            return
        if invoice.transaction_ids.filtered(
            lambda t: t._is_subscription_charge_accepted()
        ):
            # A payment for this period is in progress
            return
        if not invoice:
            with self.env.cr.savepoint():
                invoice = self._create_draft_invoice()
        self._pay_invoice(invoice)

    def _get_current_period_invoice(self):
        self.ensure_one()
        return (self.invoice_ids | self.sale_order_ids.invoice_ids).filtered(
            lambda m: m.move_type == "out_invoice"
            and m.state in ("draft", "posted")
            and m.invoice_date == self.recurring_next_date
        )[-1:]

    def _create_draft_invoice(self):
        self.ensure_one()
        if self.template_id.invoicing_mode == "sale_and_invoice":
            order = self.create_sale_order()
            order.action_confirm()
            order.action_lock()
            invoice = order._create_invoices()
            invoice.write(
                {
                    "invoice_origin": order.name + ", " + self.name,
                    "invoice_date": self.recurring_next_date,
                }
            )
            return invoice
        return self.create_invoice()

    def _pay_invoice(self, invoice):
        """Charge the invoice and post-process the payment.

        :return: the accepted transaction, empty if the charge failed.
        """
        self.ensure_one()
        transaction = self._charge_invoice(invoice)
        if not transaction:
            return transaction
        try:
            with self.env.cr.savepoint():
                self._post_process_payment(transaction)
                if invoice.payment_state not in ("paid", "in_payment"):
                    self._post_payment_note(
                        body=self._invoice_chatter_link(
                            self.env._(
                                "Automatic payment submitted; awaiting "
                                "confirmation for invoice"
                            ),
                            invoice,
                        )
                    )
        except Exception:
            # The payment cron retries the post-processing
            _logger.exception(
                "Post-processing of automatic payment %s failed",
                transaction.reference,
            )
        return transaction

    @api.model
    def _can_commit(self):
        return not (tools.config["test_enable"] or modules.module.current_test)

    def _post_process_payment(self, transaction):
        if transaction.state == "done":
            transaction._post_process()

    def _on_payment_confirmed(self, transaction, invoice):
        """Called by the payment post-processing once the invoice is paid."""
        self.ensure_one()
        label = self.env._("Automatic payment confirmed for invoice")
        already = self.message_ids.filtered(
            lambda m: label in (m.body or "")
            and transaction.reference in (m.body or "")
        )
        if not already:
            self._post_payment_note(
                body=self._invoice_chatter_link(label, invoice)
                + f" ({transaction.reference})"
            )
            if self.template_id.invoicing_mode in ("invoice", "invoice_send"):
                self._send_paid_invoice_email(invoice)
        if invoice.invoice_date == self.recurring_next_date:
            self._set_next_invoice_date_after_invoice()
        self._clear_payment_failure(transaction)

    def _get_failed_payment_invoices(self):
        """Unpaid invoices whose automatic payment failed."""
        self.ensure_one()
        invoices = (self.invoice_ids | self.sale_order_ids.invoice_ids).filtered(
            lambda m: m.move_type == "out_invoice"
            and m.state in ("draft", "posted")
            and m.payment_state in ("not_paid", "partial")
        )
        return invoices.filtered(
            lambda m: m.transaction_ids.filtered(lambda t: t.operation == "offline")
            and not m.transaction_ids.filtered(
                lambda t: t._is_subscription_charge_accepted()
            )
        )

    def action_retry_payment(self):
        for subscription in self:
            invoices = (
                subscription._get_failed_payment_invoices()
                | subscription._get_current_period_invoice().filtered(
                    lambda m: m.payment_state in ("not_paid", "partial")
                    and not m.transaction_ids.filtered(
                        lambda t: t._is_subscription_charge_accepted()
                    )
                )
            ).sorted(lambda m: (m.invoice_date or date.min, m.id))
            if not invoices:
                raise UserError(
                    self.env._(
                        "There is no failed automatic payment to retry on %s. "
                        "Clear Payment exception once the issue is resolved.",
                        subscription.display_name,
                    )
                )
            for invoice in invoices:
                if not subscription._pay_invoice(invoice):
                    break

    @api.model
    def _cron_retry_failed_payments(self):
        subscriptions = self.search(
            [
                ("payment_exception", "=", True),
                ("template_id.auto_retry_payment", "=", True),
                ("is_paused", "=", False),
            ]
        ).filtered(lambda s: s.stage_id.type != "post")
        for subscription in subscriptions:
            subscription = subscription.with_company(subscription.company_id)
            try:
                for invoice in subscription._get_invoices_to_retry_automatically():
                    transaction = subscription._pay_invoice(invoice)
                    # Persist each charge so a later error can't roll it back
                    # and lead to the customer being charged twice
                    if self._can_commit():
                        self.env.cr.commit()  # pylint: disable=invalid-commit
                    if not transaction:
                        break
            except Exception:
                if self._can_commit():
                    self.env.cr.rollback()
                _logger.exception(
                    "Error retrying the payment of subscription %s", subscription.id
                )

    def _get_invoices_to_retry_automatically(self):
        self.ensure_one()
        template = self.template_id
        now = fields.Datetime.now()
        invoices = self.env["account.move"]
        for invoice in self._get_failed_payment_invoices().sorted(
            lambda m: (m.invoice_date or date.min, m.id)
        ):
            attempts = invoice.transaction_ids.filtered(
                lambda t: t.operation == "offline"
            )
            if len(attempts) > template.auto_retry_payment_count:
                continue
            last_attempt = max(attempts.mapped("last_state_change"))
            retry_delay = timedelta(hours=template.auto_retry_payment_hours)
            if last_attempt + retry_delay <= now:
                invoices |= invoice
        return invoices

    def _post_payment_note(self, body):
        return self.message_post(
            body=body, author_id=self.env.ref("base.partner_root").id
        )

    def _invoice_chatter_link(self, msg_static, invoice):
        return Markup("%s %s") % (msg_static, invoice._get_html_link())

    def _send_invoice_email(self, invoice):
        mail_template = self.template_id.invoice_mail_template_id
        self.env["account.move.send"]._generate_and_send_invoices(
            invoice, mail_template=mail_template, sending_methods=["email"]
        )

    def _send_paid_invoice_email(self, invoice):
        try:
            with self.env.cr.savepoint():
                self.sudo()._send_invoice_email(invoice)
        except Exception:
            # Don't block the payment post-processing
            _logger.exception("Failed to send paid invoice %s", invoice.name)

    def _payment_failure_activity_summary(self):
        return self.env._("Subscription automatic payment failed")

    def _notify_customer_payment_failure(self, invoices):
        self.ensure_one()
        template = self.template_id.payment_failure_mail_template_id
        if not template:
            return
        for invoice in invoices:
            try:
                with self.env.cr.savepoint():
                    template.sudo().send_mail(invoice.id)
                    self._post_payment_note(
                        body=self._invoice_chatter_link(
                            self.env._("Payment failure email sent for invoice"),
                            invoice,
                        )
                    )
            except Exception:
                # Don't block the failure handling
                _logger.exception(
                    "Failed to send payment failure email for invoice %s", invoice.id
                )

    def _register_payment_failure(self, message, transaction=None, invoices=None):
        """Flag the subscription. ``invoices`` are given when the customer
        may be notified, i.e. not for internal errors."""
        self.ensure_one()
        transaction = transaction or self.env["payment.transaction"]
        if (
            transaction
            and self.payment_exception
            and self.payment_exception_transaction_id == transaction
        ):
            return
        self.write(
            {
                "payment_exception": True,
                "payment_exception_transaction_id": transaction.id,
            }
        )
        self._post_payment_note(message)
        summary = self._payment_failure_activity_summary()
        if not self.activity_ids.filtered(lambda a: a.summary == summary):
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=summary,
                note=message,
                user_id=self.user_id.id or self.env.uid,
            )
        if invoices:
            self._notify_customer_payment_failure(invoices)

    def _clear_payment_failure(self, transaction):
        """Clear the exception once the failed payment is resolved by
        ``transaction``. Other exceptions, e.g. a chargeback, are cleared
        manually."""
        self.ensure_one()
        if not self.payment_exception or self._get_failed_payment_invoices():
            return
        failed = self.payment_exception_transaction_id
        if (
            failed
            and failed != transaction
            and not (failed.invoice_ids & transaction.invoice_ids)
        ):
            return
        self.payment_exception = False

    def create_payment(self, invoice):
        """Charge the invoice with the subscription's payment token.

        :return: True if the payment is done or pending, False otherwise.
        """
        transaction = self._charge_invoice(invoice)
        self._post_process_payment(transaction)
        return bool(transaction)

    def _charge_invoice(self, invoice):
        """:return: the accepted transaction, empty if the charge failed."""
        self.ensure_one()
        invoice.ensure_one()
        if invoice not in self.invoice_ids | self.sale_order_ids.invoice_ids:
            raise UserError(
                self.env._(
                    "Invoice %(invoice)s does not belong to subscription "
                    "%(subscription)s.",
                    invoice=invoice.display_name,
                    subscription=self.display_name,
                )
            )
        no_transaction = self.env["payment.transaction"]
        token = self._get_payment_token()
        if not token:
            if self.payment_token_id:
                message = self.env._(
                    "Payment token %s has been removed. Set another payment token.",
                    self.payment_token_id.display_name,
                )
            else:
                message = self.env._(
                    "No payment token found for partner %s",
                    invoice.partner_id.display_name,
                )
            self._register_payment_failure(message, invoices=invoice)
            return no_transaction
        provider = token.provider_id
        if not provider.journal_id:
            self._register_payment_failure(
                self.env._(
                    "Payment provider %s has no payment journal configured.",
                    provider.display_name,
                )
            )
            return no_transaction
        payment_transaction = self.env["payment.transaction"].sudo()
        # Draft invoices have no number yet
        has_number = invoice.name and invoice.name != "/"
        reference = payment_transaction._compute_reference(
            provider.code, prefix=invoice.name if has_number else self.name
        )
        transaction = payment_transaction.create(
            {
                "provider_id": provider.id,
                "payment_method_id": token.payment_method_id.id,
                "token_id": token.id,
                "operation": "offline",
                "reference": reference,
                "amount": invoice.amount_residual
                if invoice.state == "posted"
                else invoice.amount_total,
                "currency_id": invoice.currency_id.id,
                "partner_id": invoice.partner_id.id,
                "invoice_ids": [Command.set(invoice.ids)],
            }
        )
        try:
            transaction._charge_with_token()
        except Exception:
            _logger.exception(
                "Automatic payment request failed for subscription %s", self.id
            )
            self._register_payment_failure(
                self.env._(
                    "The automatic payment request could not be sent. "
                    "Please check the payment method."
                ),
                transaction,
            )
            return no_transaction
        if transaction._is_subscription_charge_accepted():
            self._clear_payment_failure(transaction)
            return transaction
        self._register_payment_failure(
            self.env._(
                "The automatic payment was declined: %s",
                transaction.state_message or transaction.state,
            ),
            transaction,
            invoices=invoice,
        )
        return no_transaction
