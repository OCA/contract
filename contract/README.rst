.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=================================
Contracts for recurrent invoicing
=================================

This module forward-port to v10 the contracts management with recurring
invoicing functions. Also you can print and send by email contract report.

In upstream Odoo, this functionality was moved into the Enterprise edition.

Configuration
=============

To view discount field set *Discount on lines* in user access rights.

You might find that generating all pending invoices at once takes too much
time and produces some performance problems, mostly in cases where you
generate a lot of invoices in little time (i.e. when invoicing thousands
of contracts yearly, and you get to January 1st of the next year). To avoid
this bottleneck, the trick is to **increase the cron frequence and decrease
the contracts batch size**. The counterpart is that some invoices could not
be generated in the exact day you expected. To configure that:

#. Go to *Settings > Activate the developer mode*.
#. Go to *Settings > Technical > Automation > Scheduled Actions >
   Generate Recurring Invoices from Contracts > Edit > Information*.
#. Set a lower interval. For example, change *Interval Unit* to *Hours*.
#. Go to the *Technical Data* tab, and add a batch size in *Arguments*.
   For example, it should look like ``(20,)``.
#. Save.

That's it! From now on, only 20 invoices per hour will be generated.
That should take only a few seconds each hour, and shouln't block other users.

Usage
=====

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

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/110/10.0

Known issues / Roadmap
======================

* Recover states and others functional fields in Contracts.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/contract/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Carlos Dauden <carlos.dauden@tecnativa.com>
* Angel Moya <angel.moya@domatix.com>
* Dave Lasley <dave@laslabs.com>
* Vicent Cubells <vicent.cubells@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
