# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Mass Stop",
    "summary": """
        Allows to select multiple contracts to mass interrupt""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
    ],
    "data": [
        "security/security.xml",
        "wizards/contract_mass_stop.xml",
    ],
}
