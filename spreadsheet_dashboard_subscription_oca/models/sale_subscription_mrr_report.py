# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class SaleSubscriptionMrrReport(models.Model):
    """MRR change events derived from the current state of the subscriptions.

    There is no stored MRR event log in ``subscription_oca``. This SQL view
    reconstructs an approximate one from what we do have: a positive ``new``
    event at the start date of every subscription and a negative ``churn``
    event at the closing date of the closed ones (the end date when set,
    otherwise the last write date as a fallback). Cumulating ``mrr_change``
    over time therefore yields the net active MRR. Mid-life expansion and
    contraction are not tracked (that would require a real event log).
    """

    _name = "sale.subscription.mrr.report"
    _description = "Subscription MRR Evolution"
    _auto = False
    _rec_name = "subscription_id"
    _order = "event_date desc"

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
    event_date = fields.Date(string="Event date", readonly=True)
    event_type = fields.Selection(
        [("new", "New"), ("churn", "Churn")],
        string="Event type",
        readonly=True,
    )
    mrr_change = fields.Monetary(
        string="MRR change",
        currency_field="company_currency_id",
        readonly=True,
    )

    def _query(self):
        return """
            SELECT
                (sub.id * 2 + ev.n) AS id,
                sub.id AS subscription_id,
                sub.partner_id AS partner_id,
                sub.template_id AS template_id,
                sub.user_id AS user_id,
                sub.crm_team_id AS crm_team_id,
                sub.company_id AS company_id,
                sub.company_currency_id AS company_currency_id,
                ev.event_date AS event_date,
                ev.event_type AS event_type,
                ev.mrr_change AS mrr_change
            FROM sale_subscription sub
            LEFT JOIN sale_subscription_stage stage
                ON stage.id = sub.stage_id
            CROSS JOIN LATERAL (
                VALUES
                    (0, sub.date_start, 'new', sub.recurring_monthly),
                    (1, COALESCE(sub.date, sub.write_date::date), 'churn',
                        -sub.recurring_monthly)
            ) AS ev(n, event_date, event_type, mrr_change)
            WHERE sub.active = TRUE
                AND ev.event_date IS NOT NULL
                AND (ev.event_type = 'new' OR stage.type = 'post')
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"CREATE OR REPLACE VIEW {self._table} AS ({self._query()})"
        )
