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

Recurring revenue (MRR / ARR):

-   Each subscription exposes its *Monthly recurring revenue* (MRR) and
    *Annual recurring revenue* (ARR). The line subtotals (net of discount,
    excluding taxes) are normalised to a monthly amount according to the
    template recurrence and then **converted to the company currency** using
    the rate at the subscription start date. This keeps totals comparable when
    subscriptions use pricelists in different currencies.
-   Use the *Active recurring revenue* filter to restrict the figures to
    in-progress subscriptions, which reflects live recurring revenue rather
    than the theoretical value of draft or closed subscriptions.

Reporting:

-   Go to *Subscriptions > Reporting* to analyse your recurring revenue
    with pivot and graph views:
    -   *Subscriptions Analysis*: recurring revenue per line, groupable
        by customer, template, product, salesperson or start month.
    -   *MRR Breakdown*: monthly recurring revenue of the running
        subscriptions by template and product.
    -   *Churn Analysis*: closed subscriptions and the revenue lost,
        grouped by close reason.
-   All amounts are expressed in the company currency, so figures remain
    comparable when subscriptions use pricelists in other currencies.
