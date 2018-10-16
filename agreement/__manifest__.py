# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreements",
    "summary": "Manage Agreements, LOI and Contracts",
    "author": "Pavlov Media, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "category": "Partner",
    "license": "AGPL-3",
    "version": "11.0.0.0.1",
    "depends": [
        "mail",
        "sale_management"
    ],
    "data": [
        "views/reports.xml",
        "views/agreement.xml",
        "views/agreement_clause.xml",
        "views/agreement_section.xml",
        "views/agreement_stages.xml",
        "views/agreement_type.xml",
        "views/agreement_subtype.xml",
        "views/agreement_renewaltype.xml",
        "views/agreement_increasetype.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
    ],
    "application": True,
}
