# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Subscription portal",
    "summary": "Preview subscriptions in the customer portal.",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Subscription Management",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "author": "Domatix, Odoo Community Association (OCA)",
    "depends": ["subscription_oca", "portal"],
    "data": [
        "views/sale_subscription_portal_templates.xml",
        "views/sale_subscription_views.xml",
    ],
    "demo": [
        "demo/subscription_demo.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "subscription_oca_portal/static/src/interactions/subscription_sidebar.esm.js",
        ],
    },
    "installable": True,
}
