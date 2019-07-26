For example, to automate the regular creation of an invoice:

* Go to the menu *Settings > Technical > Automation > Recurring Types* and define a new document type based on the *Invoice* object.
* Go to the menu *Settings > Technical > Automation > Recurring Documents* and create a subscriptionlinked to the new document type and set the parameters of the subscription (frequency, number of documents, etc.). Then click on the *Process* button: Odoo will generate a new scheduled action (ir.cron) linked to that subscription. If you want to stop this subscription before its end or if you have set an unlimited number of documents and you want to stop or suspend it, click on the *Stop* button: Odoo will disable the related automated action.
