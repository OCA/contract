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
