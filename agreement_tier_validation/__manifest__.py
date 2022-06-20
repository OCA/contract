# Copyright 2022 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Agreement Tier Validation",
    "summary": "Extends the functionality of Agreement to "
    "support a tier validation process.",
    "version": "14.0.1.0.1",
    "category": "Contract Management",
    "website": "https://github.com/OCA/contract",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["agreement_legal", "base_tier_validation"],
    "data": ["views/agreement_view.xml"],
}
