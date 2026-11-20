This module extends *Subscription management* (`subscription_oca`) so
subscriptions can charge a customer's saved payment method (a *payment
token*) automatically on each billing run, so no manual collection step
is needed. This is intended for recurring merchant-initiated charges
(for example SEPA direct debit or a stored card via a tokenising payment
provider).

The defining principle is **charge before posting**: the invoice is kept
in *draft* and is only posted (and reconciled) once the payment
succeeds. A failed charge therefore never leaves a posted invoice owed
by the customer and never consumes an invoice number.
