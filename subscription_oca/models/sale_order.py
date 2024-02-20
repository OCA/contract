# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="sale_order_id",
        string="Subscriptions",
    )
    subscriptions_count = fields.Integer(compute="_compute_subscriptions_count")
    order_subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Subscription"
    )

    @api.depends("subscription_ids")
    def _compute_subscriptions_count(self):
        for record in self:
            record.subscriptions_count = len(record.subscription_ids)

    def action_view_subscriptions(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "name": self.name,
            "view_mode": "tree,form",
        }

    def get_next_interval(self, type_interval, interval):
        date_start = date.today()
        date_start += relativedelta(**{type_interval: interval})
        return date_start

    def create_subscription(self, lines, subscription_tmpl):
        subscription_lines = []
        for line in lines:
            subscription_lines.append((0, 0, line.get_subscription_line_values()))

        if subscription_tmpl:
            rec = self.env["sale.subscription"].create(
                {
                    "partner_id": self.partner_id.id,
                    "user_id": self._context["uid"],
                    "template_id": subscription_tmpl.id,
                    "pricelist_id": self.partner_id.property_product_pricelist.id,
                    "date_start": date.today(),
                    "sale_order_id": self.id,
                    "sale_subscription_line_ids": subscription_lines,
                }
            )
            rec.action_start_subscription()
            self.subscription_ids = [(4, rec.id)]
            rec.recurring_next_date = self.get_next_interval(
                subscription_tmpl.recurring_rule_type,
                subscription_tmpl.recurring_interval,
            )

    def group_subscription_lines(self):
        grouped = defaultdict(list)
        for order_line in self.order_line.filtered(
            lambda line: line.product_id.subscribable
        ):
            grouped[
                order_line.product_id.product_tmpl_id.subscription_template_id
            ].append(order_line)
        return grouped

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for record in self:
            grouped = self.group_subscription_lines()
            for tmpl, lines in grouped.items():
                record.create_subscription(lines, tmpl)
        return res
