# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Contract Fixed Discount",
    "version": "14.0.1.0.0",
    "category": "Contract Management",
    "author": "Foodles, Odoo Community Association (OCA)",
    "maintainers": [],
    "website": "https://github.com/OCA/contract",
    "depends": [
        "account_invoice_fixed_discount",
        "contract",
    ],
    "data": [
        "views/abstract_contract_line.xml",
        "views/contract_line.xml",
        "views/contract.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
