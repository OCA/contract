# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Slc Contract Invoice Suspended",
    "summary": """
        Contract automatic invoicing suspension""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "category": "contract",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "contract_line_successor",
        # OCA/contract
        "contract_sale",
    ],
    "data": [
        "security/acl_auto_invoice_suspension_reason.xml",
        "views/contract.xml",
        "views/auto_invoice_suspension_reason.xml",
    ],
    "installable": True,
}
