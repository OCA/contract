To use this module, you need to:

#. Go to Accounting -> Contracts and select or create a new contract.
#. Check *Generate recurring invoices automatically*.
#. Fill fields for selecting the recurrency and invoice parameters:

   * Journal
   * Pricelist
   * Period. It can be any interval of days, weeks, months, months last day or
     years.
   * Start date and next invoice date.
   * Invoicing type: pre-paid or post-paid.

#. Add the lines to be invoiced with the product, description, quantity and
   price.
#. You can mark Auto-price? for having a price automatically obtained applying
   the pricelist to the product price.
#. You have the possibility to use the markers #START# or #END# in the
   description field to show the start and end date of the invoiced period.
#. Choosing between pre-paid and post-paid, you modify the dates that are shown
   with the markers.
#. A cron is created with daily interval, but if you are in debug mode, you can
   click on *Create invoices* to force this action.
#. Click *Show recurring invoices* link to show all invoices created by the
   contract.
#. Click on *Print > Contract* menu to print contract report.
#. Click on *Send by Email* button to send contract by email.
