# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Transmit Method",
    "summary": """
        Set transmit method (email, post, portal, ...) in contracts and
        propagate it to invoices.""",
    "version": "12.0.1.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract", "account_invoice_transmit_method"],
    "data": ["views/contract_template.xml", "views/contract_contract.xml"],
}
