# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from markupsafe import Markup

from odoo import Command, api, fields, models
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
    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice address",
        compute="_compute_partner_address_ids",
        store=True,
        readonly=False,
        help="Address the recurring invoices are addressed to. "
        "Defaults to the customer's invoice address.",
    )
    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Delivery address",
        compute="_compute_partner_address_ids",
        store=True,
        readonly=False,
        help="Delivery address used on the recurring invoices and orders. "
        "Defaults to the customer's delivery address.",
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
    def _read_group_stage_ids(self, stages, domain):
        stage_ids = stages.search(domain, order=stages._order)
        return stage_ids

    stage_id = fields.Many2one(
        comodel_name="sale.subscription.stage",
        string="Stage",
        tracking=True,
        group_expand="_read_group_stage_ids",
        store=True,
    )
    stage_type = fields.Selection(
        related="stage_id.type",
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

    @api.model
    def cron_subscription_management(self):
        today = date.today()
        subscription_count = self.search_count([])
        for subscription in self.search(
            [], order="recurring_next_date asc", limit=subscription_count
        ):
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
            record.name = f"{template_code}{slash}{code}"

    @api.depends("template_id", "date_start")
    def _compute_rule_boundary(self):
        for record in self:
            # No template yet (e.g. a new record in the form view) or an
            # unlimited one: there is no end date to compute.
            if (
                not record.template_id
                or record.template_id.recurring_rule_boundary == "unlimited"
            ):
                record.date = False
                record.recurring_rule_boundary = True
            else:
                record.date = record.template_id._get_date(record.date_start)
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

    def _get_recurrence_delta(self):
        self.ensure_one()
        type_interval = self.template_id.recurring_rule_type
        interval = int(self.template_id.recurring_interval or 0) or 1
        return relativedelta(**{type_interval: interval})

    def _get_first_invoice_date(self):
        self.ensure_one()
        return self.date_start or fields.Date.today()

    def _get_next_invoice_date(self, previous_date):
        self.ensure_one()
        if isinstance(previous_date, datetime):
            previous_date = previous_date.date()
        elif not isinstance(previous_date, date):
            previous_date = fields.Date.to_date(previous_date)
        return previous_date + self._get_recurrence_delta()

    def _set_next_invoice_date_after_invoice(self, invoice_date=None):
        self.ensure_one()
        # A subscription without a scheduled next date (e.g. closed, or not
        # started yet) can still be invoiced manually: advance from its first
        # invoice date instead of crashing on a False date.
        previous_date = (
            invoice_date or self.recurring_next_date or self._get_first_invoice_date()
        )
        self.recurring_next_date = self._get_next_invoice_date(previous_date)

    def _get_contract_end_date(self):
        self.ensure_one()
        if self.template_id.recurring_rule_boundary == "unlimited":
            return False
        return self.template_id._get_date(self._get_first_invoice_date())

    def calculate_recurring_next_date(self, start_date):
        if self.account_invoice_ids_count == 0:
            if not start_date:
                start_date = self._get_first_invoice_date()
            if isinstance(start_date, datetime):
                start_date = start_date.date()
            elif not isinstance(start_date, date):
                start_date = fields.Date.to_date(start_date)
            self.recurring_next_date = start_date
        else:
            self.recurring_next_date = self._get_next_invoice_date(start_date)

    @api.depends("partner_id")
    def _compute_partner_address_ids(self):
        for subscription in self:
            if not subscription.partner_id:
                subscription.partner_invoice_id = False
                subscription.partner_shipping_id = False
                continue
            addresses = subscription.partner_id.address_get(["invoice", "delivery"])
            subscription.partner_invoice_id = addresses.get(
                "invoice", subscription.partner_id.id
            )
            subscription.partner_shipping_id = addresses.get(
                "delivery", subscription.partner_id.id
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
        self.write(
            {
                "close_reason_id": close_reason_id,
                "stage_id": closed_stage,
            }
        )

    def _prepare_sale_order(self, line_ids=False):
        self.ensure_one()
        return {
            "partner_id": self.partner_id.id,
            "partner_invoice_id": (self.partner_invoice_id.id or self.partner_id.id),
            "partner_shipping_id": (self.partner_shipping_id.id or self.partner_id.id),
            "pricelist_id": self.pricelist_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "date_order": datetime.now(),
            "payment_term_id": self.partner_id.property_payment_term_id.id,
            "user_id": self.user_id.id,
            "origin": self.name,
            "order_line": line_ids,
        }

    def _prepare_account_move(self, line_ids):
        self.ensure_one()
        # The invoice is addressed to the invoice address, like a sale order
        # invoice is created on ``partner_invoice_id``. ``commercial_partner_id``
        # still rolls up to the contracting company, so the receivable is kept
        # on the parent. ``partner_shipping_id`` is passed explicitly so it is
        # not re-derived from the (invoice) partner_id.
        invoice_partner = self.partner_invoice_id or self.partner_id
        values = {
            "partner_id": invoice_partner.id,
            "partner_shipping_id": (self.partner_shipping_id.id or self.partner_id.id),
            "invoice_date": self.recurring_next_date,
            "invoice_payment_term_id": invoice_partner.property_payment_term_id.id,
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
        if not self.env["account.move"].has_access("create"):
            try:
                self.check_access("write")
            except AccessError:
                return self.env["account.move"]
        line_ids = []
        for line in self.sale_subscription_line_ids:
            line_values = line._prepare_account_move_line()
            line_ids.append(Command.create(line_values))
        invoice_values = self._prepare_account_move(line_ids)
        invoice_id = (
            self.env["account.move"]
            .sudo()
            .with_context(default_move_type="out_invoice", journal_type="sale")
            .create(invoice_values)
        )
        return invoice_id

    def create_sale_order(self):
        if not self.env["sale.order"].has_access("create"):
            try:
                self.check_access("write")
            except AccessError:
                return self.env["sale.order"]
        line_ids = []
        for line in self.sale_subscription_line_ids:
            line_values = line._prepare_sale_order_line()
            line_ids.append(Command.create(line_values))
        values = self._prepare_sale_order(line_ids)
        order_id = self.env["sale.order"].sudo().create(values)
        self.write({"sale_order_ids": [Command.link(order_id.id)]})
        return order_id

    def generate_invoice(self):
        invoice_number = ""
        message_body = ""
        msg_static = self.env._("Created invoice with reference")
        template = self.template_id
        if template.create_sale_order:
            order_id = self.create_sale_order()
            order_id.action_confirm()
            order_id.action_lock()
            invoice = order_id._create_invoices()
            invoice.invoice_origin = order_id.name + ", " + self.name
        else:
            invoice = self.create_invoice()
        if invoice and template.invoice_state == "posted":
            invoice.action_post()
            if template.send_invoice:
                self.env["account.move.send"]._generate_and_send_invoices(
                    invoice,
                    mail_template=template.invoice_mail_template_id,
                    sending_methods=["email"],
                )
            invoice_number = invoice.name
            message_body = (
                f"<b>{msg_static}</b> "
                f"<a href=# data-oe-model=account.move data-oe-id={invoice.id}>"
                f"{invoice_number}"
                "</a>"
            )

        if not invoice_number:
            invoice_number = self.env._("To validate")
            message_body = f"<b>{msg_static}</b> {invoice_number}"
        self._set_next_invoice_date_after_invoice()
        self.message_post(body=Markup(message_body))

    def manual_invoice(self):
        invoice_id = self.create_invoice()
        self._set_next_invoice_date_after_invoice()
        context = dict(self.env.context)
        context["form_view_initial_mode"] = "edit"
        return {
            "name": self.name,
            "views": [
                (self.env.ref("account.view_move_form").id, "form"),
                (self.env.ref("account.view_move_tree").id, "list"),
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
            record.account_invoice_ids_count = len(record.invoice_ids) + len(
                record.sale_order_ids.invoice_ids
            )

    def action_view_account_invoice_ids(self):
        return {
            "name": self.name,
            "views": [
                (self.env.ref("account.view_move_tree").id, "list"),
                (self.env.ref("account.view_move_form").id, "form"),
            ],
            "view_type": "form",
            "view_mode": "list,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [
                ("id", "in", self.invoice_ids.ids + self.sale_order_ids.invoice_ids.ids)
            ],
            "context": self.env.context,
        }

    def _compute_sale_order_ids_count(self):
        data = self.env["sale.order"]._read_group(
            domain=[("order_subscription_id", "in", self.ids)],
            groupby=["order_subscription_id"],
            aggregates=["__count"],
        )
        count_dict = {
            subscription.id: count for subscription, count in data if subscription
        }
        for record in self:
            record.sale_order_ids_count = count_dict.get(record.id, 0)

    def action_view_sale_order_ids(self):
        active_ids = self.sale_order_ids.ids
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "list,form",
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
                        today = date.today()
                        record.date_start = today
                        record.calculate_recurring_next_date(today)
                    elif record.stage_id.type == "post":
                        record.close_reason_id = values.get("close_reason_id", False)
                        record.in_progress = False
                    else:
                        record.in_progress = False

        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
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
                res = self._check_dates(
                    values["date_start"], values["recurring_next_date"]
                )
                if res:
                    values["date_start"] = values["recurring_next_date"]
                values["stage_id"] = (
                    self.env["sale.subscription.stage"]
                    .search([("type", "=", "draft")], order="sequence desc", limit=1)
                    .id
                )
        return super().create(vals_list)
