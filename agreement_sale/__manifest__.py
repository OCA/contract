# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreement Sale",
    "summary": "Agreement on sales",
    "version": "13.0.1.0.0",
    "category": "Contract",
    "author": "Akretion, " "Odoo Community Association (OCA)",
    "website": "https://github.com/oca/contract",
    "license": "AGPL-3",
    "depends": ["sale_management", "agreement"],
    "data": [
        "security/ir.model.access.csv",
        "views/agreement.xml",
        "views/sale_order.xml",
        "views/res_config_settings.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["alexis-via", "bealdav"],
    "installable": True,
}
