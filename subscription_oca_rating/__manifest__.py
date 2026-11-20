# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Subscription OCA Rating",
    "summary": "Collect customer ratings on subscriptions.",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Subscription Management",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "author": "Domatix, Odoo Community Association (OCA)",
    "depends": ["subscription_oca", "rating"],
    "data": [
        "data/mail_template_data.xml",
        "views/sale_subscription_views.xml",
    ],
    "installable": True,
}
