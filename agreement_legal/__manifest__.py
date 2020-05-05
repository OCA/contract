# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreements Legal",
    "summary": "Manage Agreements, LOI and Contracts",
    "author": "Pavlov Media, "
    "Open Source Integrators, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "category": "Partner",
    "license": "AGPL-3",
    "version": "12.0.2.0.0",
    "depends": ["contacts", "agreement", "product"],
    "data": [
        "data/ir_sequence.xml",
        "data/module_category.xml",
        "data/agreement_stage.xml",
        "data/agreement_type.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "report/agreement.xml",
        "views/res_config_settings.xml",
        "views/agreement_appendix.xml",
        "views/agreement_clause.xml",
        "views/agreement_recital.xml",
        "views/agreement_section.xml",
        "views/agreement_stages.xml",
        "views/agreement_type.xml",
        "views/agreement_subtype.xml",
        "views/agreement_renewaltype.xml",
        "views/agreement_increasetype.xml",
        "views/res_partner.xml",
        "views/agreement.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/demo.xml"
    ],
    'qweb': [
        "static/src/xml/domain_widget_view.xml"
    ],
    "post_init_hook": "post_init_agreement_legal",
    "application": True,
    "development_status": "Beta",
    "maintainers": [
        "max3903",
        "ygol"
    ],
}
