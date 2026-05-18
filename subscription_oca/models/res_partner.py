# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="partner_id",
        string="Subscriptions",
    )
    subscription_count = fields.Integer(
        required=False,
        compute="_compute_subscription_count",
    )

    def _compute_subscription_count(self):
        data = self.env["sale.subscription"]._read_group(
            domain=[("partner_id", "in", self.ids)],
            groupby=["partner_id"],
            aggregates=["__count"],
        )
        count_dict = {partner.id: count for partner, count in data if partner}
        for record in self:
            record.subscription_count = count_dict.get(record.id, 0)

    def action_view_subscription_ids(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "name": self.name,
            "view_mode": "list,form",
            "context": {
                "default_partner_id": self.id,
            },
        }
