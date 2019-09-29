# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Agreement Sale Conditions and Partner Preferences (base module)",
    "summary": "Base module to manage sale conditions "
    "and partner preferences in agreements",
    "version": "12.0.1.0.0",
    # see https://odoo-community.org/page/development-status
    "development_status": "Alpha",
    "category": "Sale",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["gurneyalex"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "agreement_sale",
        "stock",
        "delivery",
    ],
    "data": [
        #  "security/sale_service_definition_security.xml",
        "security/ir.model.access.csv",
        "views/agreement.xml",
        "views/agreement_type.xml",
        "views/agreement_parameter_value.xml",
        "views/sale_order.xml",
        "views/procurement_group.xml",
        "views/res_partner.xml",
        "data/agreement_type.xml",
        "data/agreement.xml",
    ],
    'demo': [
        "demo/agreement_type.xml",
        "demo/agreement.csv",
    ],
}
