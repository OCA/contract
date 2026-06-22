# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class SaleSubscriptionRetentionReport(models.Model):
    """Retention cohorts derived from the current state of the subscriptions.

    Each subscription is expanded into one row per elapsed month between its
    start date and either its closing date (for churned ones) or today (for
    the ones still running). Grouping by ``cohort_date`` (the start month) and
    ``period_index`` (months since the start) gives a retention/survival matrix
    without needing a stored event log.
    """

    _name = "sale.subscription.retention.report"
    _description = "Subscription Retention"
    _auto = False
    _rec_name = "subscription_id"
    _order = "cohort_date desc, period_index"

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
    cohort_date = fields.Date(string="Cohort (start month)", readonly=True)
    period_index = fields.Integer(string="Months since start", readonly=True)
    recurring_monthly = fields.Monetary(
        string="Monthly recurring revenue",
        currency_field="company_currency_id",
        readonly=True,
    )

    def _query(self):
        return """
            SELECT
                (sub.id * 1000 + gs.idx) AS id,
                sub.id AS subscription_id,
                sub.partner_id AS partner_id,
                sub.template_id AS template_id,
                sub.user_id AS user_id,
                sub.crm_team_id AS crm_team_id,
                sub.company_id AS company_id,
                sub.company_currency_id AS company_currency_id,
                date_trunc('month', sub.date_start)::date AS cohort_date,
                gs.idx AS period_index,
                sub.recurring_monthly AS recurring_monthly
            FROM sale_subscription sub
            LEFT JOIN sale_subscription_stage stage
                ON stage.id = sub.stage_id
            CROSS JOIN LATERAL (
                SELECT CASE
                    WHEN stage.type = 'post'
                        THEN COALESCE(sub.date, sub.write_date::date)
                    ELSE CURRENT_DATE
                END AS d
            ) AS ref
            CROSS JOIN LATERAL generate_series(
                0,
                LEAST(
                    GREATEST(0, (
                        EXTRACT(YEAR FROM age(ref.d, sub.date_start)) * 12
                        + EXTRACT(MONTH FROM age(ref.d, sub.date_start))
                    )::int),
                    60
                )
            ) AS gs(idx)
            WHERE sub.active = TRUE
                AND sub.date_start IS NOT NULL
                AND sub.date_start <= CURRENT_DATE
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"CREATE OR REPLACE VIEW {self._table} AS ({self._query()})"
        )
