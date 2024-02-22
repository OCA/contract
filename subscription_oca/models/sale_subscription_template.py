# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    invoicing_mode = fields.Selection(
        default="draft",
        string="Invoicing mode",
        selection=[
            ("draft", "Draft"),
            ("invoice", "Invoice"),
            ("invoice_send", "Invoice & send"),
            ("sale_and_invoice", "Sale Order & Invoice"),
            ("sale_and_invoice_draft", "Sale Order & Invoice Draft"),
            ("sale_and_invoice_send", "Sale Order & Invoice send"),
            ("sale_draft", "Sale Order Draft"),
            ("sale_confirmed", "Sale Order Confirmed"),
        ],
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

    def _default_stages(self):
        return self.env["sale.subscription.stage"].search([("is_default", "=", True)])

    stage_ids = fields.Many2many(
        "sale.subscription.stage",
        string="Stages",
        default=lambda self: self._default_stages(),
    )
    days_before_expiring = fields.Integer("Days Before Expiring", default=0)
    has_expiring = fields.Boolean(store=False)

    @api.onchange("stage_ids")
    def _onchange_stage_ids(self):
        self.has_expiring = bool(
            self.stage_ids.filtered(lambda s: s.type == "expiring")
        )

    def _compute_subscription_count(self):
        data = self.env["sale.subscription"].read_group(
            domain=[("template_id", "in", self.ids)],
            fields=["template_id"],
            groupby=["template_id"],
        )
        count_dict = {
            item["template_id"][0]: item["template_id_count"] for item in data
        }
        for record in self:
            record.subscription_count = count_dict.get(record.id, 0)

    def action_view_subscription_ids(self):
        return {
            "name": self.name,
            "view_mode": "tree,form",
            "res_model": "sale.subscription",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.subscription_ids.ids)],
        }

    def _get_date(self, date_start):
        self.ensure_one()
        return relativedelta(months=+self.recurring_rule_count) + date_start

    @api.depends("product_ids")
    def _compute_product_ids_count(self):
        for record in self:
            record.product_ids_count = len(self.product_ids)

    def action_view_product_ids(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "product.template",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.product_ids.ids)],
        }

    def get_relative_delta(self):
        self.ensure_one()
        rule_type = self.recurring_rule_type
        interval = self.recurring_interval
        if rule_type == "days":
            return relativedelta(days=interval)
        elif rule_type == "weeks":
            return relativedelta(weeks=interval)
        elif rule_type == "months":
            return relativedelta(months=interval)
        else:
            return relativedelta(years=interval)

    def _check_stages_validity(self, stage_ids, duration):
        stages = self.env["sale.subscription.stage"].browse(stage_ids)
        expiring_stages = (self.stage_ids + stages).filtered(
            lambda s: s.type == "expiring"
        )
        if expiring_stages:
            if len(expiring_stages) >= 2:
                raise ValidationError(_("Can't have more than one 'expiring' stage"))
            if duration == "unlimited":
                raise ValidationError(
                    _("Can't have an unlimited duration and an 'expiring' stage")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "stage_ids" in vals.keys():
                self._check_stages_validity(
                    vals["stage_ids"][0][-1], vals["recurring_rule_boundary"]
                )
        res = super().create(vals_list)
        return res

    def write(self, vals):
        if ("stage_ids" in vals.keys()) or ("recurring_rule_boundary" in vals.keys()):
            stages = vals.get("stage_ids")
            recurring_rule_boundary = vals.get(
                "recurring_rule_boundary", self.recurring_rule_boundary
            )
            self._check_stages_validity(
                stages[0][-1] if stages else self.stage_ids.ids,
                recurring_rule_boundary,
            )
        res = super().write(vals)
        return res

    def cron_expiring_subscriptions(self):
        templates = self.search(
            [
                ("subscription_ids", "!=", False),
                ("days_before_expiring", ">", 0),
                ("stage_ids.type", "=", "expiring"),
            ]
        )
        for template in templates:
            expire_stage = template.stage_ids.filtered(lambda s: s.type == "expiring")
            for sub in template.subscription_ids.filtered(
                lambda s: s.stage_id.type in "in_progress"
            ):
                if sub.date and fields.Date.today() >= sub.date - relativedelta(
                    days=template.days_before_expiring
                ):
                    sub.stage_id = expire_stage
