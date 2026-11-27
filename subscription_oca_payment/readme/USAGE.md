## Assigning the payment token

On a subscription whose template has *Automatic payment* enabled, a
*Payment Token* field appears. It can be set in three ways:

- **Manually** - pick any saved token belonging to the customer.
- **Suggested automatically** - when you select the partner or the
  template, the customer's *Subscription Payment Token* is proposed, or
  else the most recent token saved for the customer, its company or the
  company's other contacts (in the subscription's company). A token you
  set manually is never silently overwritten.
- **Carried over from a sale** - see *Onboarding from eCommerce* below.

If the field is left empty, the customer's *Subscription Payment Token*
is charged.

A payment token that has been removed (archived), for example by the
customer from their portal, is never charged; the customer's
*Subscription Payment Token* is used instead if set, otherwise the
subscription is flagged with *Payment Exception*.

A token belonging to a different commercial partner cannot be assigned;
this is enforced by a constraint.

## What happens on each billing run

When the *Subscriptions Management* cron job generates an invoice for a
subscription with *Automatic payment*:

1.  A **draft** invoice is created for the period (or the period's draft
    left over from a failed attempt is reused, so retries never pile up
    duplicates).
2.  An offline payment transaction is created against the saved token and
    submitted to the provider.
3.  **On success** the invoice is posted, reconciled with the payment,
    and - depending on the invoicing mode - emailed to the customer as a
    paid document. The customer never receives an "amount due" document
    for money already taken. The next invoice date is then moved on.
4.  **On asynchronous capture** (e.g. direct debit) the transaction is
    left *pending* and the invoice stays draft; it is posted (and emailed,
    as above) when the provider confirms the charge, and only then is the
    next invoice date moved on. Until then the subscription is not
    invoiced again.
5.  **On failure** the invoice stays draft, the subscription is flagged
    (see *Payment failures*) and the next invoice date is **not**
    advanced, so the same period is retried once the issue is fixed.

The *Create Invoice* button on a subscription does **not** charge the
token: it creates a draft invoice and advances the next invoice date, as
it does without automatic payment.

## Use cases

- **Stored-card billing (synchronous)** - the charge is captured
  immediately; the invoice is posted, reconciled and emailed in the same
  run.
- **Direct debit / asynchronous capture** - the charge is *submitted*
  and the provider confirms it later via webhook; the invoice is posted
  and emailed on confirmation.
- **Silent background billing** - use *Draft* mode with *Automatic
  payment* to collect and post without ever emailing the customer.
- **Onboarding from a webshop sale** - see below.

## Payment failures

If a charge cannot be collected (no token, a provider without a journal,
the request could not be sent, or the provider rejects it), or the
provider later reports that an accepted payment failed or was cancelled
(for example a failed direct debit), the subscription is:

- flagged with *Payment Exception*, showing the *Failed Payment*, with a
  chatter note giving the provider's reason,
- emailed, if a *Payment Failure Email* is set on the template (not for
  configuration errors such as a provider without a journal),
- given a **to-do activity** (visible in the list and kanban views) so a
  salesperson is alerted, and
- left with an unpaid invoice: a draft one, or a posted one whose payment
  was cancelled.

While the flag is set, the cron job **skips** the subscription, so a
broken payment method does not generate repeated invoices or charges.
Use the *Payment exception* filter to list them.

Once the payment method has been fixed, either:

- click **Retry payment** to charge the unpaid invoices again, oldest
  first. The flag and the activity are cleared as soon as the provider
  accepts the payment (a pending direct debit counts). This also works
  after the automatic retries below have been used up, or
- clear *Payment Exception* to resume invoicing; the current period's
  draft is then charged on the next run. Clearing the flag also resolves
  the activity.

If *Retry failed payments* is ticked on the template, a scheduled
action also charges failed invoices again automatically, up to the
configured number of retries. After the last retry the flag stays set
for a salesperson to follow up.

If the provider retries the payment itself (for example a direct-debit
resubmission) and it succeeds, the flag is cleared automatically. A
provider module that reports a payment it is retrying as *pending*
doesn't flag the subscription at all. If yours reports it as failed
while still retrying, don't click **Retry payment** or clear *Payment
Exception*: the customer could be charged twice. Wait until the provider
reports that it has stopped retrying.

Chargebacks don't change the payment's state, so they only flag the
subscription if the payment provider module reports them by calling
`payment.transaction._subscription_payment_reversed()`. Otherwise,
handle them in the payment provider. The invoice stays paid, so there is
nothing to retry: follow up the reinstated debt, and clear *Payment
Exception* manually if the subscription was flagged.

## Onboarding from eCommerce

A customer's first token is typically captured when they buy a
subscription product online and pay with a tokenising provider. When the
sale order is confirmed:

1.  A subscription is created from the order's subscribable products (via
    their *Subscription template*), as usual.
2.  If that template has *Automatic payment* enabled, the token saved
    during the order's online payment is copied onto the new
    subscription automatically.

From the next billing cycle onward the subscription charges that token
without any manual setup.
