.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=================================================
Variable quantity in contract recurrent invoicing
=================================================

With this module, you will be able to define in recurring contracts some
lines with variable quantity according to a provided formula.

Configuration
=============

#. Go to Sales > Configuration > Contracts > Formulas (quantity).
#. Define any formula based on Python code that stores at some moment a
   float/integer value of the quantity to invoice in the variable 'result'.

   You can use these variables to compute your formula:

   * *env*: Environment variable for getting other models.
   * *context*: Current context dictionary.
   * *user*: Current user.
   * *line*: Contract recurring invoice line that triggers this formula.
   * *contract*: Contract whose line belongs to.
   * *invoice*: Invoice (header) being created.

.. figure:: images/formula_form.png
   :alt: Formula form
   :width: 600 px

Usage
=====

To use this module, you need to:

#. Go to Sales -> Contracts and select or create a new contract.
#. Check *Generate recurring invoices automatically*.
#. Add a new recurring invoicing line.
#. Select "Variable quantity" in column "Qty. type".
#. Select one of the possible formulas to use (previously created).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/110/9.0

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
