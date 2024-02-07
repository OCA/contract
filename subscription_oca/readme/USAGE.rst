To make a subscription:

#. Go to *Subscriptions > Configuration > Subscription templates*.
#. Create the templates you consider, choosing the billing frequency: daily, monthly... and the method of creating the invoice and/or order.
#. Go to *Subscription > Subscriptions*.
#. Create a subscription and indicate the start date. When the *Subscriptions Management* cron job is executed, the subscription will begin and the first invoice will be created if the execution date matches the start date. The invoice will also be created when the execution date matches the next invoice date. Additionally, you can manually change the subscription status and create an invoice by using the *Create Invoice* button. This action creates just an invoice even if the subscription template has the *Sale Order & Invoice* option selected, because the *Invoicing mode* option is triggered through the cron job.
#. The cron job will also end the subscription if its end date has been reached.

To create subscriptions with the sale of a product:

#. Go to *Subscriptions > Subscriptions > Products*.
#. Create the product and in the sales tab, complete the fields *Subscribable product* and *Subscription template*
#. Create a sales order with the product and confirm it.
