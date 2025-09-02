# Copyright 2024 Kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        help="Employee associated with this contract (for freelancers/contractors)",
        domain="[('employee_type', 'in', ['freelance', 'contractor'])]",
    )

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        help="Department of the employee",
    )

    job_id = fields.Many2one(
        comodel_name="hr.job",
        string="Job Position",
        help="Job position of the employee",
    )

    # Computed fields
    employee_name = fields.Char(
        string="Employee Name", related="employee_id.name", store=True, readonly=True
    )

    employee_work_email = fields.Char(
        string="Work Email", related="employee_id.work_email", store=True, readonly=True
    )

    employee_work_phone = fields.Char(
        string="Work Phone", related="employee_id.work_phone", store=True, readonly=True
    )

    employee_type = fields.Selection(
        related="employee_id.employee_type",
        string="Employee Type",
        store=True,
        readonly=True,
    )

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        """Update department and job when employee changes"""
        if self.employee_id:
            self.department_id = self.employee_id.department_id
            self.job_id = self.employee_id.job_id
        else:
            self.department_id = False
            self.job_id = False
