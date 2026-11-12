1.  Configure a payment provider that supports tokenisation and set its
    *Payment Journal*. Charges cannot be made through a provider without
    a journal.
2.  Go to *Subscriptions \> Configuration \> Subscription templates* and
    open or create a template.
3.  Pick an *Invoicing mode* (see the table below for how each one
    behaves once automatic payment is on).
4.  Tick *Automatic payment*.
5.  Optionally, set the settings that appear below it:
    - *Payment Failure Email*: emailed to the customer when an automatic
      payment fails. Empty by default; the *Subscription: Automatic
      Payment Failure* template is provided. Leave it empty if the
      payment provider already notifies the customer (GoCardless does).
    - *Retry failed payments*: unticked by default. When ticked, a
      failed payment is charged again automatically, up to *Payment
      retries* times (default 3), *Hours between retries* apart
      (default 24). Leave it unticked if the payment provider retries
      failed payments itself (for example GoCardless), otherwise the
      customer could be charged twice.

Optionally, a default payment token can be set on the customer, in the
*Sales & Purchase* tab of the contact (*Subscription Payment Token*). It
is charged for subscriptions with automatic payment that have no
*Payment Token* of their own.

*Automatic payment* is orthogonal to the invoicing mode and works with
**all** of them, including *Draft*.

| Invoicing mode | On a successful charge |
|---|---|
| *Draft* | Invoice posted, **no email** (silent background billing) |
| *Invoice* | Invoice posted, paid invoice emailed |
| *Invoice & send* | Invoice posted, paid invoice emailed |
| *Sale order & Invoice* | Sale order confirmed, invoice posted (no email) |

The paid invoice is emailed once by the subscription, also when the
*Automatic Invoice* setting of *Sales* is enabled.
