# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract State",
    "summary": "Draft/active workflow for contracts, gating invoice generation",
    "version": "19.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "bosd, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "maintainers": ["bosd"],
    "depends": ["contract"],
    "data": [
        "security/contract_security.xml",
        "views/contract.xml",
        "views/contract_portal_templates.xml",
    ],
    "installable": True,
}
