# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class SaleSubscriptionReport(models.Model):
    _name = "sale.subscription.report"
    _description = "Subscription Analysis"
    _auto = False
    _rec_name = "subscription_id"
    _order = "date_start desc"

    subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Subscription", readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer", readonly=True
    )
    template_id = fields.Many2one(
        comodel_name="sale.subscription.template",
        string="Subscription template",
        readonly=True,
    )
    stage_id = fields.Many2one(
        comodel_name="sale.subscription.stage", string="Stage", readonly=True
    )
    stage_type = fields.Selection(
        [
            ("draft", "Draft"),
            ("pre", "Ready to start"),
            ("in_progress", "In progress"),
            ("post", "Closed"),
        ],
        string="Stage type",
        readonly=True,
    )
    close_reason_id = fields.Many2one(
        comodel_name="sale.subscription.close.reason",
        string="Close Reason",
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users", string="Commercial agent", readonly=True
    )
    crm_team_id = fields.Many2one(
        comodel_name="crm.team", string="Sale team", readonly=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency", string="Company Currency", readonly=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", readonly=True
    )
    categ_id = fields.Many2one(
        comodel_name="product.category", string="Product Category", readonly=True
    )
    in_progress = fields.Boolean(string="In progress", readonly=True)
    to_renew = fields.Boolean(string="To renew", readonly=True)
    date_start = fields.Date(string="Start date", readonly=True)
    date_end = fields.Date(string="Finish date", readonly=True)
    recurring_next_date = fields.Date(string="Next invoice date", readonly=True)
    product_uom_qty = fields.Float(string="Quantity", readonly=True)
    recurring_monthly = fields.Monetary(
        string="Monthly recurring revenue",
        currency_field="company_currency_id",
        readonly=True,
    )
    recurring_yearly = fields.Monetary(
        string="Annual recurring revenue",
        currency_field="company_currency_id",
        readonly=True,
    )

    def _select(self):
        return """
            SELECT
                line.id AS id,
                sub.id AS subscription_id,
                sub.partner_id AS partner_id,
                sub.template_id AS template_id,
                sub.stage_id AS stage_id,
                stage.type AS stage_type,
                sub.close_reason_id AS close_reason_id,
                sub.user_id AS user_id,
                sub.crm_team_id AS crm_team_id,
                sub.company_id AS company_id,
                sub.company_currency_id AS company_currency_id,
                line.product_id AS product_id,
                template.categ_id AS categ_id,
                sub.in_progress AS in_progress,
                sub.to_renew AS to_renew,
                sub.date_start AS date_start,
                sub.date AS date_end,
                sub.recurring_next_date AS recurring_next_date,
                line.product_uom_qty AS product_uom_qty,
                line.recurring_monthly AS recurring_monthly,
                line.recurring_monthly * 12.0 AS recurring_yearly
        """

    def _from(self):
        return """
            FROM sale_subscription_line line
            JOIN sale_subscription sub
                ON sub.id = line.sale_subscription_id
            LEFT JOIN sale_subscription_stage stage
                ON stage.id = sub.stage_id
            LEFT JOIN product_product product
                ON product.id = line.product_id
            LEFT JOIN product_template template
                ON template.id = product.product_tmpl_id
            WHERE sub.active = TRUE
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"CREATE OR REPLACE VIEW {self._table} AS ({self._select()} {self._from()})"
        )
