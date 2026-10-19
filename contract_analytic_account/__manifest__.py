# Copyright 2026 Cristiano Mafra Junior - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Contract Analytic Account",
    "summary": "Set an analytic distribution on the contract and propagate it to its lines",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Contract Management",
    "website": "https://github.com/OCA/contract",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "maintainers": ["CristianoMafraJunior"],
    "license": "AGPL-3",
    "depends": ["contract", "project"],
    "data": [
        "views/contract_view.xml",
        "views/project_view.xml",
    ],
    "installable": True,
}
