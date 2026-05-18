# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import Command, api, fields, models
from odoo.exceptions import UserError


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
        data = self.env["sale.subscription"]._read_group(
            domain=[("sale_order_id", "in", self.ids)],
            groupby=["sale_order_id"],
            aggregates=["__count"],
        )
        count_dict = {sale_order.id: count for sale_order, count in data if sale_order}
        for record in self:
            record.subscriptions_count = count_dict.get(record.id, 0)

    def action_view_subscriptions(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "name": self.name,
            "view_mode": "list,form",
        }

    def get_next_interval(self, type_interval, interval):
        date_start = date.today()
        date_start += relativedelta(**{type_interval: interval})
        return date_start

    def create_subscription(self, lines, subscription_tmpl):
        self.ensure_one()
        if subscription_tmpl:
            pricelist = (
                self.pricelist_id
                or self.partner_id.with_company(
                    self.company_id
                ).property_product_pricelist
                or self.partner_id.property_product_pricelist
                or self.env["product.pricelist"].search(
                    [("company_id", "in", [False, self.company_id.id])],
                    limit=1,
                )
            )
            if not pricelist:
                raise UserError(
                    self.env._("No pricelist found to create subscription.")
                )
            subscription_lines = [
                Command.create(line.get_subscription_line_values()) for line in lines
            ]
            rec = self.env["sale.subscription"].create(
                {
                    "partner_id": self.partner_id.id,
                    "user_id": self.env.context.get("uid", self.env.uid),
                    "template_id": subscription_tmpl.id,
                    "pricelist_id": pricelist.id,
                    "date_start": date.today(),
                    "sale_order_id": self.id,
                    "sale_subscription_line_ids": subscription_lines,
                }
            )
            rec.action_start_subscription()
            rec.recurring_next_date = self.get_next_interval(
                subscription_tmpl.recurring_rule_type,
                subscription_tmpl.recurring_interval,
            )

    def group_subscription_lines(self):
        """
        Group Sale Order Lines by their product's subscription template
        """
        grouped = defaultdict(list)
        for order_line in self.order_line.filtered(
            lambda line: line.product_id.subscribable
        ):
            grouped[
                order_line.product_id.product_tmpl_id.subscription_template_id
            ].append(order_line)
        return grouped

    def action_confirm(self):
        """
        Create a subscription per template from the Order's products
        """
        res = super().action_confirm()
        for record in self:
            grouped = record.group_subscription_lines()
            for tmpl, lines in grouped.items():
                record.create_subscription(lines, tmpl)
        return res
