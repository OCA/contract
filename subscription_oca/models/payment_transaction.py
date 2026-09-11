# Copyright 2026 Open User Systems
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from markupsafe import Markup

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _post_process(self):
        res = super()._post_process()
        self._subscription_oca_log_confirmation()
        return res

    def _set_canceled(self, state_message=None, extra_allowed_states=()):
        res = super()._set_canceled(
            state_message=state_message, extra_allowed_states=extra_allowed_states
        )
        self._subscription_oca_flag_cancellation()
        return res

    def _subscription_oca_log_confirmation(self):
        """Post a closing chatter note on the subscription once an automatic
        payment is captured and its invoice is posted, with the real invoice
        number. Fires for both the synchronous ``done`` result and the
        asynchronous webhook confirmation, so a pending charge always gets a
        follow-up instead of a perpetual "awaiting confirmation".
        """
        for transaction in self.filtered(
            lambda t: t.state == "done" and t.operation == "offline"
        ):
            posted = transaction.invoice_ids.filtered(
                lambda m: m.state == "posted" and m.name
            )
            for invoice in posted:
                for subscription in invoice.subscription_id.filtered(
                    "auto_create_payment"
                ):
                    label = subscription.env._(
                        "Automatic payment confirmed for invoice"
                    )
                    already = subscription.message_ids.filtered(
                        lambda m, lbl=label, name=invoice.name: lbl in (m.body or "")
                        and name in (m.body or "")
                    )
                    if already:
                        continue
                    subscription.sudo().message_post(
                        body=Markup(subscription._invoice_chatter_link(label, invoice))
                    )

    def _subscription_oca_flag_cancellation(self):
        """Surface a cancelled/reversed automatic payment on its subscription.

        When an offline subscription charge is cancelled later (a permanent
        direct-debit failure, or a chargeback that the payment framework
        unreconciles), nothing otherwise tells the subscription: it keeps
        looking paid and the scheduler keeps billing. Flag the subscription
        (exception + to-do activity + chatter) so the event is not missed.

        Only the subscription's own status is touched: the invoice is left to
        the payment framework (a draft stays draft; a posted invoice is
        unreconciled when its payment is cancelled), the stage is left alone,
        and the next-invoice date is not reset (a posted invoice already stands
        as the receivable for that period).
        """
        for transaction in self.filtered(lambda t: t.operation != "refund"):
            subscriptions = transaction.invoice_ids.subscription_id.filtered(
                "auto_create_payment"
            )
            for subscription in subscriptions:
                subscription.sudo()._register_payment_failure(
                    self.env._(
                        "The automatic payment (%s) was cancelled or reversed. "
                        "Any posted invoice for this period is no longer paid "
                        "and may need to be followed up or refunded."
                    )
                    % transaction.reference
                )
