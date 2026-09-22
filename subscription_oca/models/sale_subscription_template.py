# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleSubscriptionTemplate(models.Model):
    _name = "sale.subscription.template"
    _description = "Subscription templates"

    name = fields.Char(required=True)
    description = fields.Text(string="Terms and conditions")
    recurring_interval = fields.Integer(string="Repeat every", default=1)
    recurring_rule_type = fields.Selection(
        [
            ("days", "Day(s)"),
            ("weeks", "Week(s)"),
            ("months", "Month(s)"),
            ("years", "Year(s)"),
        ],
        string="Recurrence",
        default="months",
    )
    recurring_rule_boundary = fields.Selection(
        [("unlimited", "Forever"), ("limited", "Fixed")],
        string="Duration",
        default="unlimited",
    )
    create_sale_order = fields.Boolean(
        string="Create sale order",
        help="Generate a confirmed sale order before invoicing. Required for the "
        "subscription to appear in Sales analysis reports.",
    )
    invoice_state = fields.Selection(
        selection=[("draft", "Draft"), ("posted", "Posted")],
        string="Invoice status",
        default="draft",
        required=True,
        help="State in which the generated invoice is left.",
    )
    send_invoice = fields.Boolean(
        string="Send invoice by email",
        help="Send the invoice by email once posted, using the template below.",
    )
    code = fields.Char()
    recurring_rule_count = fields.Integer(default=1, string="Rule count")
    invoice_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Invoice Email",
        domain="[('model', '=', 'account.move')]",
    )
    product_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="subscription_template_id",
        string="Products",
    )
    product_ids_count = fields.Integer(
        compute="_compute_product_ids_count", string="product_ids"
    )
    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="template_id",
        string="Subscriptions",
    )
    subscription_count = fields.Integer(
        compute="_compute_subscription_count", string="subscription_ids"
    )

    def _compute_subscription_count(self):
        data = self.env["sale.subscription"]._read_group(
            domain=[("template_id", "in", self.ids)],
            groupby=["template_id"],
            aggregates=["__count"],
        )
        count_dict = {template.id: count for template, count in data if template}
        for record in self:
            record.subscription_count = count_dict.get(record.id, 0)

    def action_view_subscription_ids(self):
        return {
            "name": self.name,
            "view_mode": "list,form",
            "res_model": "sale.subscription",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.subscription_ids.ids)],
        }

    def _get_date(self, date_start):
        self.ensure_one()
        delta_type = self.recurring_rule_type or "months"
        interval = (self.recurring_interval or 1) * self.recurring_rule_count
        return date_start + relativedelta(**{delta_type: interval})

    @api.depends("product_ids")
    def _compute_product_ids_count(self):
        for record in self:
            record.product_ids_count = len(record.product_ids)

    def action_view_product_ids(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "list,form",
            "res_model": "product.template",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.product_ids.ids)],
        }
