# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Minimum Term",
    "summary": "Minimum term, renewal term and termination notice for contracts",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Callino,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "maintainers": ["wpichler"],
    "depends": ["contract_termination"],
    "data": [
        "security/groups.xml",
        "data/ir_cron.xml",
        "views/contract_template.xml",
        "views/contract_template_line.xml",
        "views/contract_contract.xml",
        "views/contract_line.xml",
        "wizards/contract_contract_terminate.xml",
    ],
}
