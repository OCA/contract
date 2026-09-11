To make a subscription:

1.  Go to *Subscriptions \> Configuration \> Subscription templates*.
2.  Create the templates you consider, choosing the billing frequency:
    daily, monthly... and the method of creating the invoice and/or
    order.
3.  Go to *Subscription \> Subscriptions*.
4.  Create a subscription and indicate the start date. When the
    *Subscriptions Management* cron job is executed, the subscription
    will begin and the first invoice will be created if the execution
    date matches the start date. The invoice will also be created when
    the execution date matches the next invoice date. Additionally, you
    can manually change the subscription status and create an invoice by
    using the *Create Invoice* button. This action creates just an
    invoice even if the subscription template has the *Sale Order &
    Invoice* option selected, because the *Invoicing mode* option is
    triggered through the cron job.
5.  The cron job will also end the subscription if its end date has been
    reached.

To create subscriptions with the sale of a product:

1.  Go to *Subscriptions \> Subscriptions \> Products*.
2.  Create the product and in the sales tab, complete the fields
    *Subscribable product* and *Subscription template*
3.  Create a sales order with the product and confirm it.

## Automatic payment

Subscriptions can charge a customer's saved payment method (a
*payment token*) automatically on each billing run, so no manual
collection step is needed. This is intended for recurring
merchant-initiated charges (for example SEPA direct debit or a stored
card via a tokenizing payment provider).

The defining principle is **charge before posting**: the invoice is kept
in *draft* and is only posted (and reconciled) once the payment
succeeds. A failed charge therefore never leaves a posted invoice owed
by the customer and never consumes an invoice number.

### Enabling it on a template

1.  Go to *Subscriptions \> Configuration \> Subscription templates* and
    open or create a template.
2.  Pick an *Invoicing mode* (see the table below for how each one
    behaves once automatic payment is on).
3.  Tick *Automatic payment*.

*Automatic payment* is orthogonal to the invoicing mode and works with
**all** of them, including *Draft*.

### Assigning the payment token

On a subscription whose template has *Automatic payment* enabled, a
*Payment Token* field appears. It can be set in three ways:

- **Manually** - pick any saved token belonging to the customer.
- **Suggested automatically** - when you select the partner, the most
  recent token saved for that partner (in the subscription's company) is
  proposed. A token you set manually is never silently overwritten.
- **Carried over from a sale** - see *Onboarding from eCommerce* below.

A token belonging to a different commercial partner cannot be assigned;
this is enforced by a constraint.

### What happens on each billing run

When the *Subscriptions Management* cron job (or a manual run) generates
an invoice for a subscription with *Automatic payment*:

1.  A **draft** invoice is created (or a draft left over from a previous
    failed attempt is reused, so retries never pile up duplicates).
2.  An offline payment transaction is created against the saved token and
    submitted to the provider.
3.  **On success** the invoice is posted, reconciled with the payment,
    and - depending on the invoicing mode - emailed to the customer as a
    paid document. The customer never receives an "amount due" document
    for money already taken.
4.  **On asynchronous capture** (e.g. direct debit) the transaction is
    left *pending* and the invoice stays draft; it is posted later when
    the provider confirms the charge via webhook. The subscription keeps
    billing normally.
5.  **On failure** the invoice stays draft, the subscription is flagged
    (see *Payment failures*) and the next invoice date is **not**
    advanced, so the same period is retried once the issue is fixed.

### Invoicing mode behaviour with automatic payment

| Invoicing mode | On a successful charge |
|---|---|
| *Draft* | Invoice posted, **no email** (silent background billing) |
| *Invoice* | Invoice posted, paid invoice emailed |
| *Invoice & send* | Invoice posted, paid invoice emailed |
| *Sale order & Invoice* | Sale order confirmed, invoice posted (no email) |

### Use cases

- **Stored-card billing (synchronous)** - the charge is captured
  immediately; the invoice is posted, reconciled and emailed in the same
  run.
- **Direct debit / asynchronous capture** - the charge is *submitted*
  and the provider confirms it later via webhook; the invoice is posted
  on confirmation.
- **Silent background billing** - use *Draft* mode with *Automatic
  payment* to collect and post without ever emailing the customer.
- **Onboarding from a webshop sale** - see below.

### Payment failures

If a charge cannot be collected (no token, a misconfigured provider, or
the provider rejects it outright) the subscription is:

- flagged with *Payment Exception*,
- given a **to-do activity** (visible in the list and kanban views) so a
  salesperson is alerted, and
- left with its draft invoice and unchanged next-invoice date.

While the flag is set, the cron job **skips** the subscription, so a
broken payment method does not generate repeated invoices or charges.
Once the payment method has been fixed, clear *Payment Exception* (the
activity is resolved automatically on the next successful charge) and the
subscription resumes. Integrations that manage their own retries (for
example a direct-debit provider) can set or clear this flag through the
same field.

### Onboarding from eCommerce

A customer's first token is typically captured when they buy a
subscription product online and pay with a tokenizing provider. When the
sale order is confirmed:

1.  A subscription is created from the order's subscribable products (via
    their *Subscription template*), as usual.
2.  If that template has *Automatic payment* enabled, the token saved
    during the order's online payment is copied onto the new
    subscription automatically.

From the next billing cycle onward the subscription charges that token
without any manual setup.
