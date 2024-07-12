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
