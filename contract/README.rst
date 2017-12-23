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
