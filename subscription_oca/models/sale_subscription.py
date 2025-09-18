# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    color = fields.Integer("Color Index")
    name = fields.Char(
        compute="_compute_name",
        store=True,
    )
    sequence = fields.Integer()
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", required=True, string="Partner", index=True
    )
    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )
    active = fields.Boolean(default=True)
    template_id = fields.Many2one(
        comodel_name="sale.subscription.template",
        required=True,
        string="Subscription template",
    )
    code = fields.Char(
        string="Reference",
        default=lambda self: self.env["ir.sequence"].next_by_code("sale.subscription"),
    )
    in_progress = fields.Boolean(string="In progress", default=False)
    recurring_rule_boundary = fields.Boolean(
        string="Boundary", compute="_compute_rule_boundary", store=True
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist", required=True, string="Pricelist"
    )
    recurring_next_date = fields.Date(string="Next invoice date", default=date.today())
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Commercial agent",
        default=lambda self: self.env.user.id,
    )
    date_start = fields.Date(string="Start date", default=date.today())
    date = fields.Date(
        string="Finish date",
        compute="_compute_rule_boundary",
        store=True,
        readonly=False,
    )
    description = fields.Text()
    sale_order_id = fields.Many2one(
        comodel_name="sale.order", string="Origin sale order"
    )
    terms = fields.Text(
        string="Terms and conditions",
        compute="_compute_terms",
        store=True,
        readonly=False,
    )
    invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="subscription_id",
        string="Invoices",
    )
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="order_subscription_id",
        string="Orders",
    )
    recurring_total = fields.Monetary(
        compute="_compute_total", string="Recurring price", store=True
    )
    amount_tax = fields.Monetary(compute="_compute_total", store=True)
    amount_total = fields.Monetary(compute="_compute_total", store=True)
    tag_ids = fields.Many2many(comodel_name="sale.subscription.tag", string="Tags")
    image = fields.Binary("Image", related="user_id.image_512", store=True)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")
    currency_id = fields.Many2one(
        related="pricelist_id.currency_id",
        depends=["pricelist_id"],
        store=True,
        ondelete="restrict",
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages.search([], order=order)
        return stage_ids

    stage_id = fields.Many2one(
        comodel_name="sale.subscription.stage",
        string="Stage",
        tracking=True,
        group_expand="_read_group_stage_ids",
        store=True,
    )
    stage_str = fields.Char(
        related="stage_id.name",
        string="Etapa",
        store=True,
    )
    sale_subscription_line_ids = fields.One2many(
        comodel_name="sale.subscription.line",
        inverse_name="sale_subscription_id",
    )
    sale_order_ids_count = fields.Integer(
        compute="_compute_sale_order_ids_count", string="Sale orders"
    )
    account_invoice_ids_count = fields.Integer(
        compute="_compute_account_invoice_ids_count", string="Invoice Count"
    )
    close_reason_id = fields.Many2one(
        comodel_name="sale.subscription.close.reason", string="Close Reason"
    )
    crm_team_id = fields.Many2one(comodel_name="crm.team", string="Sale team")
    to_renew = fields.Boolean(default=False, string="To renew")

    def cron_subscription_management(self):
        today = date.today()
        for subscription in self.search([], order="recurring_next_date asc"):
            subscription = subscription.with_company(subscription.company_id)
            if subscription.in_progress:
                if (
                    subscription.recurring_next_date <= today
                    and subscription.sale_subscription_line_ids
                ):
                    try:
                        subscription.generate_invoice()
                    except Exception:
                        logger.exception("Error on subscription invoice generate")
                if (
                    not subscription.recurring_rule_boundary
                    and subscription.date <= today
                ):
                    subscription.close_subscription()

            elif (
                subscription.date_start <= today and subscription.stage_id.type == "pre"
            ):
                subscription.action_start_subscription()
                subscription.generate_invoice()

    @api.depends("sale_subscription_line_ids")
    def _compute_total(self):
        for record in self:
            recurring_total = amount_tax = 0.0
            for order_line in record.sale_subscription_line_ids:
                recurring_total += order_line.price_subtotal
                amount_tax += order_line.amount_tax_line_amount
            record.update(
                {
                    "recurring_total": recurring_total,
                    "amount_tax": amount_tax,
                    "amount_total": recurring_total + amount_tax,
                }
            )

    @api.depends("template_id", "code")
    def _compute_name(self):
        for record in self:
            template_code = record.template_id.code if record.template_id.code else ""
            code = record.code if record.code else ""
            slash = "/" if template_code and code else ""
            record.name = "{}{}{}".format(template_code, slash, code)

    @api.depends("template_id", "date_start")
    def _compute_rule_boundary(self):
        for record in self:
            if record.template_id.recurring_rule_boundary == "unlimited":
                record.date = False
                record.recurring_rule_boundary = True
            else:
                record.date = (
                    relativedelta(months=+record.template_id.recurring_rule_count)
                    + record.date_start
                )
                record.recurring_rule_boundary = False

    @api.depends("template_id")
    def _compute_terms(self):
        for record in self:
            record.terms = record.template_id.description

    @api.onchange("template_id", "date_start")
    def _onchange_template_id(self):
        today = date.today()
        if self.date_start:
            today = self.date_start
        if self.template_id and self.account_invoice_ids_count > 0:
            self.calculate_recurring_next_date(self.recurring_next_date)
        else:
            self.calculate_recurring_next_date(today)

    def calculate_recurring_next_date(self, start_date):
        if self.account_invoice_ids_count == 0:
            self.recurring_next_date = date.today()
        else:
            type_interval = self.template_id.recurring_rule_type
            interval = int(self.template_id.recurring_interval)
            self.recurring_next_date = start_date + relativedelta(
                **{type_interval: interval}
            )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id_fpos(self):
        self.fiscal_position_id = (
            self.env["account.fiscal.position"]
            .with_company(self.company_id)
            ._get_fiscal_position(self.partner_id)
        )

    def action_start_subscription(self):
        self.close_reason_id = False
        in_progress_stage = self.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )
        self.stage_id = in_progress_stage

    def action_close_subscription(self):
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "close.reason.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": False,
        }

    def close_subscription(self, close_reason_id=False):
        self.ensure_one()
        self.recurring_next_date = False
        closed_stage = self.env["sale.subscription.stage"].search(
            [("type", "=", "post")], limit=1
        )
        self.close_reason_id = close_reason_id
        self.stage_id = closed_stage

    def _prepare_sale_order(self, line_ids=False):
        self.ensure_one()
        return {
            "partner_id": self.partner_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "date_order": datetime.now(),
            "payment_term_id": self.partner_id.property_payment_term_id.id,
            "user_id": self.user_id.id,
            "origin": self.name,
            "order_line": line_ids,
        }

    def _prepare_account_move(self, line_ids):
        self.ensure_one()
        values = {
            "partner_id": self.partner_id.id,
            "invoice_date": self.recurring_next_date,
            "invoice_payment_term_id": self.partner_id.property_payment_term_id.id,
            "invoice_origin": self.name,
            "invoice_user_id": self.user_id.id,
            "partner_bank_id": self.company_id.partner_id.bank_ids[:1].id,
            "invoice_line_ids": line_ids,
            "subscription_id": self.id,
        }
        if self.journal_id:
            values["journal_id"] = self.journal_id.id
        return values

    def create_invoice(self):
        if not self.env["account.move"].check_access_rights("create", False):
            try:
                self.check_access_rights("write")
                self.check_access_rule("write")
            except AccessError:
                return self.env["account.move"]
        line_ids = []
        for line in self.sale_subscription_line_ids:
            line_values = line._prepare_account_move_line()
            line_ids.append((0, 0, line_values))
        invoice_values = self._prepare_account_move(line_ids)
        invoice_id = (
            self.env["account.move"]
            .sudo()
            .with_context(default_move_type="out_invoice", journal_type="sale")
            .create(invoice_values)
        )
        return invoice_id

    def create_sale_order(self):
        if not self.env["sale.order"].check_access_rights("create", False):
            try:
                self.check_access_rights("write")
                self.check_access_rule("write")
            except AccessError:
                return self.env["sale.order"]
        line_ids = []
        for line in self.sale_subscription_line_ids:
            line_values = line._prepare_sale_order_line()
            line_ids.append((0, 0, line_values))
        values = self._prepare_sale_order(line_ids)
        order_id = self.env["sale.order"].sudo().create(values)
        self.write({"sale_order_ids": [(4, order_id.id)]})
        return order_id

    def generate_invoice(self):
        invoice_number = ""
        msg_static = _("Created invoice with reference")
        if self.template_id.invoicing_mode in ["draft", "invoice", "invoice_send"]:
            invoice = self.create_invoice()
            if self.template_id.invoicing_mode != "draft":
                invoice.action_post()
                if self.template_id.invoicing_mode == "invoice_send":
                    mail_template = self.template_id.invoice_mail_template_id
                    invoice.with_context(force_send=True).message_post_with_template(
                        mail_template.id,
                        composition_mode="comment",
                        email_layout_xmlid="mail.mail_notification_paynow",
                    )
                    invoice.write({"is_move_sent": True})
                invoice_number = invoice.name
                message_body = (
                    "<b>%s</b> <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>"
                    % (msg_static, invoice.id, invoice_number)
                )

        if self.template_id.invoicing_mode == "sale_and_invoice":
            order_id = self.create_sale_order()
            order_id.action_done()
            new_invoice = order_id._create_invoices()
            new_invoice.action_post()
            new_invoice.invoice_origin = order_id.name + ", " + self.name
            invoice_number = new_invoice.name
            message_body = (
                "<b>%s</b> <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>"
                % (msg_static, new_invoice.id, invoice_number)
            )
        if not invoice_number:
            invoice_number = _("To validate")
            message_body = "<b>%s</b> %s" % (msg_static, invoice_number)
        self.calculate_recurring_next_date(self.recurring_next_date)
        self.message_post(body=message_body)

    def manual_invoice(self):
        invoice_id = self.create_invoice()
        self.calculate_recurring_next_date(self.recurring_next_date)
        context = dict(self.env.context)
        context["form_view_initial_mode"] = "edit"
        return {
            "name": self.name,
            "views": [
                (self.env.ref("account.view_move_form").id, "form"),
                (self.env.ref("account.view_move_tree").id, "tree"),
            ],
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": invoice_id.id,
            "type": "ir.actions.act_window",
            "context": context,
        }

    @api.depends("invoice_ids", "sale_order_ids.invoice_ids")
    def _compute_account_invoice_ids_count(self):
        for record in self:
            record.account_invoice_ids_count = len(self.invoice_ids) + len(
                self.sale_order_ids.invoice_ids
            )

    def action_view_account_invoice_ids(self):
        return {
            "name": self.name,
            "views": [
                (self.env.ref("account.view_move_tree").id, "tree"),
                (self.env.ref("account.view_move_form").id, "form"),
            ],
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [
                ("id", "in", self.invoice_ids.ids + self.sale_order_ids.invoice_ids.ids)
            ],
            "context": self.env.context,
        }

    def _compute_sale_order_ids_count(self):
        data = self.env["sale.order"].read_group(
            domain=[("order_subscription_id", "in", self.ids)],
            fields=["order_subscription_id"],
            groupby=["order_subscription_id"],
        )
        count_dict = {
            item["order_subscription_id"][0]: item["order_subscription_id_count"]
            for item in data
        }
        for record in self:
            record.sale_order_ids_count = count_dict.get(record.id, 0)

    def action_view_sale_order_ids(self):
        active_ids = self.sale_order_ids.ids
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", active_ids)],
            "context": self.env.context,
        }

    def _check_dates(self, start, next_invoice):
        if start and next_invoice:
            date_start = start
            date_next_invoice = next_invoice
            if not isinstance(date_start, date) and not isinstance(
                date_next_invoice, date
            ):
                date_start = fields.Date.to_date(start)
                date_next_invoice = fields.Date.to_date(next_invoice)
            if date_start > date_next_invoice:
                return True
        return False

    def write(self, values):
        res = super().write(values)
        if "stage_id" in values:
            for record in self:
                if record.stage_id:
                    if record.stage_id.type == "in_progress":
                        record.in_progress = True
                        record.date_start = date.today()
                    elif record.stage_id.type == "post":
                        record.close_reason_id = False
                        record.in_progress = False
                    else:
                        record.in_progress = False

        return res

    @api.model
    def create(self, values):
        if "recurring_rule_boundary" in values:
            if not values["recurring_rule_boundary"]:
                template_id = self.env["sale.subscription.template"].browse(
                    values["template_id"]
                )
                date_start = values["date_start"]
                if not isinstance(values["date_start"], date):
                    date_start = fields.Date.to_date(values["date_start"])
                values["date"] = template_id._get_date(date_start)
        if "date_start" in values and "recurring_next_date" in values:
            res = self._check_dates(values["date_start"], values["recurring_next_date"])
            if res:
                values["date_start"] = values["recurring_next_date"]
            values["stage_id"] = (
                self.env["sale.subscription.stage"]
                .search([("type", "=", "draft")], order="sequence desc", limit=1)
                .id
            )
        return super(SaleSubscription, self).create(values)
