# Copyright 2025 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class Subscription(models.Model):
    _inherit = "sale.subscription"

    def generate_invoice(self):
        """
        Generate and post an invoice for a subscription, handling the
        "recurring_payment" invoicing mode or delegating to the parent
        implementation for other modes.
        When the subscription's template has invoicing_mode == 'recurring_payment',
        this method will:
        - create an invoice for the current record (self.create_invoice()).
        - post the invoice to validate it (invoice.action_post()).
        - create/record a payment for the posted invoice (self._create_payment).
        - update the recurring next date using the value of self.recurring_next_date
            (self.calculate_recurring_next_date(self.recurring_next_date)).
        - post a chatter message on the subscription with a link/reference to the
            created invoice.
        For any other invoicing_mode, this method forwards the call to
        super().generate_invoice(subscription, date=date).
        Args:
                subscription: recordset
                        The subscription record (sale.subscription) for which
                        to generate the
                        invoice. Used for partner information and for posting messages.
                date: date or str or None
                        Optional date parameter forwarded to the superclass
                        implementation when
                        not handling the 'recurring_payment' mode. When handling
                        'recurring_payment' this implementation does not use the date
                        parameter directly.
        Returns:
                account.move or whatever the superclass returns
                        When handling 'recurring_payment', the created and posted invoice
                        record (account.move) is the effective result. Otherwise the return
                        value is whatever super().generate_invoice returns.
        Side effects:
        - Creates and posts an invoice and a corresponding payment immediately.
        - Updates the subscription's next recurring date.
        - Posts a chatter message linking to the created invoice.
        Notes:
        - This method is an override of the subscription invoicing flow and is
            intended for automatic immediate payment of recurring invoices.
        - Ensure that required helper methods/fields exist on self:
            create_invoice, _create_payment, calculate_recurring_next_date,
            recurring_next_date, template_id, and message_post.
        - The implementation must ensure the chatter message body is constructed
            before calling message_post to avoid posting an empty or incorrect message.
        """

        msg_static = _("Created invoice with reference")
        if self.template_id.invoicing_mode == "recurring_payment":
            invoice = self.create_invoice()
            invoice.action_post()
            self.create_payment(invoice)
            self.calculate_recurring_next_date(self.recurring_next_date)
            message_body = (
                "<b>%s</b> <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>"
                % (msg_static, invoice.id, invoice.name)
            )
            self.message_post(body=message_body)
            return
        else:
            return super().generate_invoice()

    def create_payment(self, invoice):
        """
        Create and execute a payment for the given invoice using
        the partner's most recent payment token.
        This helper:
        - Finds the most recent payment.token for the invoice partner.
        - Locates an account.payment.method.line that matches the token
        provider code and the invoice company.
        - Builds a payment registration payload (currency, journal,
        partner, amount, token, etc.).
        - Uses account.payment.register (with the invoice set in the context)
        to create and execute the payment(s),
            which will post payments and attempt reconciliation
            against the invoice.
        Parameters:
                invoice (account.move): The invoice (customer bill) to be paid.
                Expected to be a single record.
        Side effects:
        - Creates account.payment.register and account.payment records.
        - Posts payments and performs reconciliation according to the payment
        registration behavior.
        - Uses fields.Date.today() as the payment_date and pays the full
        invoice.amount_total.
        Exceptions:
        - Raises odoo.exceptions.UserError if no payment.token is found for the
        invoice partner.
        - May raise other ORM/validation errors if no suitable
        account.payment.method.line is found,
            the payment register fails, or required permissions are missing.
        Notes:
        - The function relies on payment.token.provider_id.code matching
        payment_method_id.code on the
            account.payment.method.line for the invoice's company.
        - The method does not explicitly return a value (returns None);
        its primary effect is to create and post payments.
        """
        self.ensure_one()

        def _last_payment_token(self, partner):
            return self.env["payment.token"].search(
                [("partner_id", "=", partner.id)], order="create_date desc", limit=1
            )

        payment_token = _last_payment_token(self, invoice.partner_id)
        if not payment_token:
            self.message_post(
                body=_(
                    "No payment token found for partner %s" % invoice.partner_id.name
                )
            )
            return

        provider = payment_token.provider_id
        method_line = self.env["account.payment.method.line"].search(
            [
                ("payment_method_id.code", "=", provider.code),
                ("company_id", "=", invoice.company_id.id),
            ],
            limit=1,
        )

        payment_register = self.env["account.payment.register"]
        payment_vals = {
            "currency_id": invoice.currency_id.id,
            "journal_id": provider.journal_id.id,
            "company_id": invoice.company_id.id,
            "partner_id": invoice.partner_id.id,
            "communication": invoice.name,
            "payment_type": "inbound",
            "partner_type": "customer",
            "payment_difference_handling": "open",
            "writeoff_label": "Write-Off",
            "payment_date": fields.Date.today(),
            "amount": invoice.amount_total,
            "payment_method_line_id": method_line.id,
            "payment_token_id": payment_token.id,
        }
        payment_register.with_context(
            active_model="account.move",
            active_ids=invoice.ids,
            active_id=invoice.id,
        ).create(payment_vals).action_create_payments()
