# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Contract Variable Qty Timesheet",
    "summary": "Add formula to invoice ",
    "version": "15.0.1.0.0",
    "category": "Contract Management",
    "website": "https://github.com/OCA/contract",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["contract_variable_quantity", "hr_timesheet"],
    "data": ["data/contract_line_qty_formula_data.xml"],
    "maintainers": ["carlosdauden", "pedrobaeza"],
}
