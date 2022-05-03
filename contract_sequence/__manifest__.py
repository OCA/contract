# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Sequence",
    "version": "14.0.0.0.1",
    "author": "Apulia Software, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "category": "Contract",
    "depends": ["contract"],
    "data": [
        "data/contract_sequence.xml",
        "views/contract.xml",
        "views/contract_template.xml",
        "views/res_config_settings_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
