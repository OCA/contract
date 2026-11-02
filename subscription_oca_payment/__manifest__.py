# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Subscription Payments",
    "summary": "Automatically charge subscription invoices to a saved payment token",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Subscription Management",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "author": "Open User Systems, Odoo Community Association (OCA)",
    "maintainers": ["chrisandrewmann"],
    "depends": ["subscription_oca", "account_payment"],
    "data": [
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        "views/res_partner_views.xml",
        "views/sale_subscription_template_views.xml",
        "views/sale_subscription_views.xml",
    ],
    "installable": True,
}
