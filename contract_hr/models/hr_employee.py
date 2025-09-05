# Copyright 2024 Kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # One2many relationship to show contracts for this employee
    contract_contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="employee_id",
        string="Freelancer/Contractor Contracts",
        domain="[('employee_id', '=', id), "
        "('employee_type', 'in', ['freelance', 'contractor'])]",
    )

    contract_contract_count = fields.Integer(
        string="Contract Count", compute="_compute_contract_contract_count"
    )

    # Computed field to show active contracts
    active_contract_contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="employee_id",
        string="Active Freelancer/Contractor Contracts",
        domain="[('employee_id', '=', id), "
        "('employee_type', 'in', ['freelance', 'contractor']), "
        "('state', '=', 'open')]",
    )

    active_contract_contract_count = fields.Integer(
        string="Active Contract Count",
        compute="_compute_active_contract_contract_count",
    )

    @api.depends("contract_contract_ids")
    def _compute_contract_contract_count(self):
        """Compute the total number of freelancer contracts"""
        for employee in self:
            employee.contract_contract_count = len(employee.contract_contract_ids)

    @api.depends("active_contract_contract_ids")
    def _compute_active_contract_contract_count(self):
        """Compute the number of active freelancer contracts"""
        for employee in self:
            employee.active_contract_contract_count = len(
                employee.active_contract_contract_ids
            )
