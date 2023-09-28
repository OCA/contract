# Copyright 2019 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Contract Price Revision",
    "summary": "Easy revision of contract prices",
    "version": "15.0.1.0.0",
    "category": "Contract",
    "author": "ACSONE SA/NV, Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract"],
    "data": [
        "security/ir.model.access.csv",
        "views/contract_line.xml",
        "wizards/contract_price_revision_views.xml",
    ],
    "installable": True,
    "development_status": "Production/Stable",
    "maintainers": ["carlosdauden"],
}
