# Copyright (C) 2018 Pavlov Media
# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Maintenance Agreements",
    "summary": "Manage maintenance agreements and contracts",
    "author": "Pavlov Media, "
    "Open Source Integrators, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "category": "Maintenance",
    "license": "AGPL-3",
    "version": "14.0.1.2.0",
    "depends": [
        "maintenance",
        "agreement_serviceprofile",
    ],
    "data": [
        "views/agreement_view.xml",
        "views/agreement_serviceprofile_view.xml",
        "views/maintenance_request_view.xml",
        "views/maintenance_equipment_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
