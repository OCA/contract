# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProductContractConfigurator(models.TransientModel):
    _name = "product.contract.configurator"
    _description = "Product Contract Configurator Wizard"

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
    recurring_rule_type = fields.Selection(related="product_id.recurring_rule_type")
    recurring_invoicing_type = fields.Selection(
        related="product_id.recurring_invoicing_type"
    )
    date_start = fields.Date()
    date_end = fields.Date()
    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line to replace",
        required=False,
    )
    is_auto_renew = fields.Boolean(
        string="Auto Renew",
        compute="_compute_auto_renew",
        default=False,
        store=True,
        readonly=False,
    )
    auto_renew_interval = fields.Integer(
        default=1,
        string="Renew Every",
        compute="_compute_auto_renew",
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
        compute="_compute_auto_renew",
        store=True,
        readonly=False,
        string="Renewal type",
        help="Specify Interval for automatic renewal.",
    )
    contract_start_date_method = fields.Selection(
        related="product_id.contract_start_date_method"
    )

    @api.depends("product_id", "company_id")
    def _compute_contract_template_id(self):
        for rec in self:
            rec.contract_template_id = rec.product_id.with_company(
                rec.company_id
            ).property_contract_template_id

    @api.depends("product_id")
    def _compute_auto_renew(self):
        for rec in self:
            if rec.product_id.is_contract:
                rec.product_uom_qty = rec.product_id.default_qty
                contract_start_date_method = rec.product_id.contract_start_date_method
                if contract_start_date_method == "manual":
                    rec.date_start = rec.date_start or fields.Date.today()
                rec.date_end = rec._get_date_end()
                rec.is_auto_renew = rec.product_id.is_auto_renew
                if rec.is_auto_renew:
                    rec.auto_renew_interval = rec.product_id.auto_renew_interval
                    rec.auto_renew_rule_type = rec.product_id.auto_renew_rule_type

    def _get_auto_renew_rule_type(self):
        """monthly last day don't make sense for auto_renew_rule_type"""
        self.ensure_one()
        if self.recurring_rule_type == "monthlylastday":
            return "monthly"
        return self.recurring_rule_type

    def _get_date_end(self):
        self.ensure_one()
        contract_line_model = self.env["contract.line"]
        date_end = (
            self.date_start
            + contract_line_model.get_relative_delta(
                self._get_auto_renew_rule_type(),
                int(self.product_uom_qty),
            )
            - relativedelta(days=1)
        )
        return date_end

    @api.onchange("date_start", "product_uom_qty")
    def _onchange_date_start(self):
        for rec in self.filtered("product_id.is_contract"):
            rec.date_end = rec._get_date_end() if rec.date_start else False
