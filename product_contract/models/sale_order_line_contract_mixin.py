# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrderLineContractMixin(models.AbstractModel):
    _name = "sale.order.line.contract.mixin"
    _description = "Sale Order Line Contract Mixin"

    is_contract = fields.Boolean(
        string="Is a contract", related="product_id.is_contract"
    )
    product_id = fields.Many2one("product.product")
    partner_id = fields.Many2one("res.partner")
    company_id = fields.Many2one("res.company")
    product_uom_qty = fields.Float("Quantity")
    contract_id = fields.Many2one(comodel_name="contract.contract", string="Contract")
    contract_template_id = fields.Many2one(
        comodel_name="contract.template",
        string="Contract Template",
        compute="_compute_contract_template_id",
    )
    recurrence_number = fields.Integer(
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
    recurrence_interval = fields.Selection(
        [
            ("monthly", "Month(s)"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        help="Specify Interval for contract duration.",
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
    recurring_interval = fields.Integer(
        default=1,
        string="Invoice Every",
        help="Invoice every (Days/Week/Month/Year)",
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
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
        string="Recurrence",
        help="Specify Interval for automatic invoice generation.",
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
    recurring_invoicing_type = fields.Selection(
        [("pre-paid", "Pre-paid"), ("post-paid", "Post-paid")],
        default="pre-paid",
        string="Invoicing type",
        help=(
            "Specify if the invoice must be generated at the beginning "
            "(pre-paid) or end (post-paid) of the period."
        ),
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )
    date_start = fields.Date(
        compute="_compute_contract_line_date_start",
        store=True,
        readonly=False,
        precompute=True,
    )
    date_end = fields.Date(
        compute="_compute_contract_line_date_end",
        store=True,
        readonly=False,
        precompute=True,
    )
    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line to replace",
        required=False,
    )
    is_auto_renew = fields.Boolean(
        string="Auto Renew",
        compute="_compute_product_contract_data",
        precompute=True,
        default=False,
        store=True,
        readonly=False,
    )
    auto_renew_interval = fields.Integer(
        default=1,
        string="Renew Every",
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
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
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
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
        compute="_compute_product_contract_data",
        precompute=True,
        store=True,
        readonly=False,
    )

    @api.depends("product_id", "company_id")
    def _compute_contract_template_id(self):
        for rec in self:
            rec.contract_template_id = rec.product_id.with_company(
                rec.company_id
            ).property_contract_template_id

    @api.depends("product_id")
    def _compute_product_contract_data(self):
        for rec in self:
            vals = {
                "recurrence_number": 0,
                "recurring_interval": 0,
                "recurring_rule_type": False,
                "recurring_invoicing_type": False,
                "recurrence_interval": False,
                "is_auto_renew": False,
                "auto_renew_interval": False,
                "auto_renew_rule_type": False,
                "contract_start_date_method": False,
            }
            if rec.product_id.is_contract:
                p = rec.product_id
                vals = {
                    "recurrence_number": p.recurrence_number,
                    "recurring_interval": p.recurring_interval,
                    "recurring_rule_type": p.recurring_rule_type,
                    "recurring_invoicing_type": p.recurring_invoicing_type,
                    "recurrence_interval": p.recurrence_interval,
                    "is_auto_renew": p.is_auto_renew,
                    "auto_renew_interval": p.auto_renew_interval,
                    "auto_renew_rule_type": p.auto_renew_rule_type,
                    "contract_start_date_method": p.contract_start_date_method,
                }
            rec.update(vals)

    @api.depends("contract_start_date_method")
    def _compute_contract_line_date_start(self):
        for rec in self:
            if rec.contract_start_date_method == "manual":
                rec.date_start = rec.date_start or fields.Date.today()

    @api.depends("date_start", "recurrence_interval", "recurrence_number")
    def _compute_contract_line_date_end(self):
        for rec in self:
            rec.date_end = rec._get_date_end() if rec.date_start else False

    def _get_date_end(self):
        self.ensure_one()
        contract_line_model = self.env["contract.line"]
        date_end = (
            self.date_start
            + contract_line_model.get_relative_delta(
                self.recurrence_interval, self.recurrence_number
            )
            - relativedelta(days=1)
        )
        return date_end
