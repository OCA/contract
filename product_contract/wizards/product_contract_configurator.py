# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


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
    recurring_interval = fields.Integer(
        default=1,
        string="Invoice Every",
        help="Invoice every (Days/Week/Month/Year)",
    )
    recurring_rule_type = fields.Selection(related="product_id.recurring_rule_type")
    recurring_invoicing_type = fields.Selection(
        related="product_id.recurring_invoicing_type"
    )
    date_start = fields.Date()
    date_end = fields.Date(compute="_compute_date_end", readonly=False, store=True)
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
    avoid_create_contract = fields.Boolean()

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
                rec.is_auto_renew = rec.product_id.is_auto_renew
                if rec.is_auto_renew:
                    rec.auto_renew_interval = rec.product_id.auto_renew_interval
                    rec.auto_renew_rule_type = rec.product_id.auto_renew_rule_type

    @api.depends("date_start", "recurring_interval")
    def _compute_date_end(self):
        self.update({"date_end": False})
        for rec in self.filtered(lambda ln: ln.is_auto_renew and ln.date_start):
            rec.date_end = self.env["contract.line"]._get_first_date_end(
                rec.date_start, rec.auto_renew_rule_type, rec.auto_renew_interval
            )
