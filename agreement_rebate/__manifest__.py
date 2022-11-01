# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Agreement Rebate",
    "summary": "Rebate in agreements",
    "version": "13.0.1.0.1",
    "development_status": "Beta",
    "category": "Contract",
    "website": "https://github.com/OCA/agreement",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "account_invoice_refund_link", "agreement"],
    "data": [
        "data/agreement_rebate_data.xml",
        "security/agreement_rebate_security.xml",
        "security/ir.model.access.csv",
        "views/agreement_condition_view.xml",
        "views/agreement_view.xml",
        "views/agreement_rebate_settlement_view.xml",
        "views/agreement_type.xml",
        "wizards/invoice_create_views.xml",
        "wizards/settlement_create_views.xml",
        "views/agreement_menu_view.xml",
    ],
}
