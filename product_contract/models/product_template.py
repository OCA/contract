# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_contract = fields.Boolean("Is a contract")
    property_contract_template_id = fields.Many2one(
        comodel_name="contract.template",
        string="Contract Template",
        company_dependent=True,
    )
    default_qty = fields.Integer(string="Default Quantity", default=1)
    recurring_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Invoice Every",
        help="Specify Interval for automatic invoice generation.",
    )
    recurring_invoicing_type = fields.Selection(
        [("pre-paid", "Pre-paid"), ("post-paid", "Post-paid")],
        default="pre-paid",
        string="Invoicing type",
        help="Specify if process date is 'from' or 'to' invoicing date",
    )
    is_auto_renew = fields.Boolean(string="Auto Renew", default=False)
    termination_notice_interval = fields.Integer(
        default=1, string="Termination Notice Before"
    )
    termination_notice_rule_type = fields.Selection(
        [("daily", "Day(s)"), ("weekly", "Week(s)"), ("monthly", "Month(s)")],
        default="monthly",
        string="Termination Notice type",
    )
    auto_renew_interval = fields.Integer(
        default=1,
        string="Renew Every",
        help="Renew every (Days/Week/Month/Year)",
    )
    auto_renew_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("yearly", "Year(s)"),
        ],
        default="yearly",
        string="Renewal type",
        help="Specify Interval for automatic renewal.",
    )
    contract_start_date_method = fields.Selection(
        [
            ("manual", "Manual"),
            ("start_this", "Start of current period"),
            ("end_this", "End of current period"),
            ("start_next", "Start of next period"),
            ("end_next", "End of next period"),
        ],
        "Start Date Method",
        default="manual",
        help="""This field allows to define how the start date of the contract will
        be calculated:

        - Manual: The start date will be selected by the user, by default will be the
        date of sale confirmation.
        - Start of current period: The start date will be the first day of the actual
        period selected on 'Invoicing Every' field. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2024/01/01.
        - End of current period: The start date will be the last day of the actual
        period selected on 'Invoicing Every' field. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2024/12/31.
        - Start of next period: The start date will be the first day of the next
        period selected on 'Invoicing Every' field. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2025/01/01.
        - End of next period: The start date will be the last day of the actual
        period selected on 'Invoicing Every' field. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2025/12/31.
        """,
    )
    force_month_yearly = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        "Force Month",
    )
    force_month_quarterly = fields.Selection(
        [
            ("1", "First month"),
            ("2", "Second month"),
            ("3", "Third month"),
        ],
        "Force Month",
        help="Force the month to be used inside the quarter",
    )
    force_month_semesterly = fields.Selection(
        [
            ("1", "First month"),
            ("2", "Second month"),
            ("3", "Third month"),
            ("4", "Fourth month"),
            ("5", "Fifth month"),
            ("6", "Sixth month"),
        ],
        "Force Month",
        help="Force the month to be used inside the semester",
    )

    def write(self, vals):
        if "is_contract" in vals and vals["is_contract"] is False:
            for company in self.env["res.company"].search([]):
                self.with_company(company).write(
                    {"property_contract_template_id": False}
                )
        return super().write(vals)

    @api.constrains("is_contract", "type")
    def _check_contract_product_type(self):
        """
        Contract product should be service type
        """
        if any([product.is_contract and product.type != "service" for product in self]):
            raise ValidationError(_("Contract product should be service type"))
