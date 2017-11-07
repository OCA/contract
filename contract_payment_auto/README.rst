.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Contract Auto Payment
=====================

This module allows for the configuration of automatic payments on invoices that are created by a contract.

Usage
=====

Enable Automatic Payment
------------------------

* Navigate to a customer contract
* Check the `Auto Pay?` box to enable automatic payment
* Configure the options as desired
* Set the `Payment Token` to the payment token that should be used for automatic payment

Automatic Payment Settings
--------------------------

The following settings are available at both the contract and contract template level:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Name                  | Description                                                                                                                                   |
+=======================+===============================================================================================================================================+
| Invoice Message       | Message template that is used to send invoices to customers upon creation.                                                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Payment Retry Message | Message template that is used to alert a customer that their automatic payment failed for some reason and will be retried.                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Payment Fail Message  | Message template that is used to alert a customer that their automatic payment failed and will no longer be retried.                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Auto Pay Retries      | Amount of times to attempt an automatic payment before discontinuing and removing the payment token from the contract/account payment method. |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Auto Pay Retry Hours  | Amount of hours that should lapse until retrying failed payments.                                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+

Payment Token
-------------

A valid payment token is required to use this module. These tokens are typically created during the `website_sale` checkout process, but they can also be created manually at the acquirer.

A payment token can be defined in one of two areas:

* Contract - Defining a payment token in the contract will allow for the use of this token for automatic payments on this contract only.
* Partner - Defining a payment token in the partner will allow for the use of this token for automatic payments on all contracts for this partner that do not have a payment token defined.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/110/10.0

Known issues / Roadmap
======================

* None

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/contract/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Dave Lasley <dave@laslabs.com>


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
