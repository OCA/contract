# Copyright 2015 Domatix (<www.domatix.com>)
# Copyright 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017-2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Contract Payment Mode",
    "summary": "Payment mode in contracts and their invoices",
    "version": "14.0.1.0.0",
    "author": "Domatix, " "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract", "account_payment_partner"],
    "category": "Sales Management",
    "license": "AGPL-3",
    "data": ["views/contract_view.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": True,
}
