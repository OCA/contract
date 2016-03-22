.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=================================
Contracts for recurrent invoicing
=================================

This module forward-port to v9 the contracts management with recurring
invoicing functions.

Configuration
=============

To view discount field set *Discount on lines* in user access rights.

Usage
=====

To use this module, you need to:

#. Go to Sales -> Contracts and select or create a new contract.
#. Check *Generate recurring invoices automatically*.
#. Fill fields and add new lines. You have the possibility to use markers in
   the description field to show the start and end date of the invoiced period.
#. A cron is created with daily interval, but if you are in debug mode can
   click on *Create invoices* to force this action.
#. Click *Show recurring invoices* link to show all invoices created by the
   contract.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/110/9.0

Known issues / Roadmap
======================

* Recovery states and others functional fields in Contracts.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/contract/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/contract/issues/new?body=module:%20contract%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Carlos Dauden <carlos.dauden@tecnativa.com>
* Angel Moya <angel.moya@domatix.com>

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
