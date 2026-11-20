# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _post_process(self):
        subscription_txs = self.filtered(lambda t: t._get_auto_payment_subscriptions())
        # The paid invoice email is sent by the subscription, not by sale
        super(
            PaymentTransaction,
            subscription_txs.with_context(skip_sale_auto_invoice_send=True),
        )._post_process()
        res = super(PaymentTransaction, self - subscription_txs)._post_process()
        # Every state change is post-processed, so this is the single place
        # reacting to the outcome of a subscription payment.
        for transaction in subscription_txs:
            if transaction.state == "done":
                transaction._subscription_payment_confirmed()
            elif transaction.state in ("error", "cancel"):
                transaction._subscription_payment_failed()
        return res

    def _is_subscription_charge_accepted(self):
        """Whether the provider accepted the charge; it may be confirmed later."""
        self.ensure_one()
        return self.state in ("pending", "authorized", "done")

    def _get_auto_payment_subscriptions(self):
        self.ensure_one()
        if self.operation != "offline":
            return self.env["sale.subscription"]
        return self.invoice_ids._get_auto_payment_subscriptions()

    def _subscription_payment_confirmed(self):
        self.ensure_one()
        for invoice in self.invoice_ids.filtered(
            lambda m: m.state == "posted" and m.payment_state in ("in_payment", "paid")
        ):
            for subscription in invoice._get_auto_payment_subscriptions():
                subscription.sudo()._on_payment_confirmed(self, invoice)

    def _subscription_payment_failed(self):
        self.ensure_one()
        if self.invoice_ids.transaction_ids.filtered(
            lambda t: t.operation == "offline" and t.id > self.id
        ):
            # Superseded by a newer attempt, e.g. a retry
            return
        message = self.env._(
            "The automatic payment %(reference)s failed or was cancelled. The "
            "invoice is not paid; use Retry payment once the payment method is "
            "fixed. Reason: %(reason)s",
            reference=self.reference,
            reason=self.state_message or self.state,
        )
        for subscription in self._get_auto_payment_subscriptions():
            subscription.sudo()._register_payment_failure(
                message, self, invoices=self.invoice_ids
            )

    def _subscription_payment_reversed(self, message):
        """Flag the subscriptions paid by these transactions after a reversal
        that doesn't change the transaction state, e.g. a chargeback. Meant
        to be called by payment providers."""
        for transaction in self:
            for subscription in transaction._get_auto_payment_subscriptions():
                subscription.sudo()._register_payment_failure(message, transaction)
