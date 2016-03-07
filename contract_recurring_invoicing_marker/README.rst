.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Markers for contract recurring invoices
=======================================

This module allows to include some markers on the lines of your recurring
invoices definition inside the contract so that the generated invoice lines
will contain a dynamic text depending on these markers.

These markers are the supported ones:

* #START#: Start date of the invoiced period.
* #END# End date of the invoiced period.

Usage
=====

On a contract (*Sales > Sales > Contracts*), mark "Generate recurring invoices
automatically" for enabling the creation of recurring invoices.

In the "Invoice Lines" section, you can add lines with products. In the
*Description* field, you can now add any of the markers mentioned before
between the rest of the text.

When you invoice this contract (automatically or manually), your invoice
will contain the corresponding text that replaces the marker.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/110/8.0

Known issues / Roadmap
======================

* Add more markers, like #START_MONTH# or #END_MONTH#.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
contract/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
contract/issues/new?body=module:%20
contract_recurring_invoicing_markers%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

Icon
----

* https://openclipart.org/detail/125071/pie-graph
* Subicon made by `Freepik <http://www.flaticon.com/authors/freepik>_ from
  www.flaticon.com

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
