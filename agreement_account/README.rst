.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Agreement (Account)
===================

This module adds an *Agreement* object with the following properties:

* type (*Sale* or *Purchase*),
* link to a partner,
* name,
* code,
* signature date.

You can link an invoice to an agreement.

If you also install the module *agreement_sale*, you will be able to link a quotation/sale order to an agreement, and this information will be copied to the customer invoice.

An *Agreement* can be used for:

* Private business contracts
* Public markets

It will allow you to group all the orders and invoices related to the same agreement and display the references of this agreement on the documents where you have to display it. For example, the *code* property of the agreement is used in the module *account_invoice_factur-x* (from the `edi <https://github.com/OCA/edi>`_ project) in the XML tag */CrossIndustryInvoice/SupplyChainTradeTransaction/ApplicableHeaderTradeAgreement/ContractReferencedDocument/IssuerAssignedID*.

The main differences with the *Contract* object of Odoo:

* a contract is an analytic account; an agreement is not related to analytic accounting.
* on the invoice, the contract/analytic account is per-line; an agreement is attached to the invoice (not to the lines).
* an agreement is a very simple object with just a few basic fields; a contract has a lot of properties and a lot of related features.

Configuration
=============

Go to the menu *Accounting > Configuration > Management > Agreements* to create new agreements.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/110/10.0

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

* Alexis de Lattre <alexis.delattre@akretion.com>

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
