# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)


{
    "name": "Contracts Management - Recurring Sales",
    "version": "14.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, PESOL, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_sale"],
    "data": [
        "data/contract_cron.xml",
        "views/contract.xml",
    ],
    "installable": True,
}
