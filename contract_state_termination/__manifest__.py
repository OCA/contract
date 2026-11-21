# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract State Termination",
    "summary": "Show terminated contracts as a Terminated state",
    "version": "19.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "bosd, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "maintainers": ["bosd"],
    "depends": ["contract_state", "contract_termination"],
    "data": ["views/contract.xml"],
    "post_init_hook": "post_init_hook",
    "auto_install": True,
    "installable": True,
}
