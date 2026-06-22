# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Subscription OCA Spreadsheet Dashboards",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Domatix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "category": "Productivity/Dashboard",
    "summary": "Spreadsheet dashboards for subscriptions (MRR, salesperson)",
    "depends": ["spreadsheet_dashboard", "subscription_oca"],
    "data": [
        "security/ir.model.access.csv",
        "report/sql_report_views.xml",
        "data/spreadsheet_dashboards.xml",
    ],
    "auto_install": True,
    "development_status": "Beta",
}
