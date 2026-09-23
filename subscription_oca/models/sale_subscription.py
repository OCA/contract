# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from markupsafe import Markup

from odoo import Command, api, fields, models
from odoo.exceptions import AccessError, ValidationError

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
    recurring_next_date = fields.Date(
        string="Next invoice date",
        default=lambda self: fields.Date.context_today(self),
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Commercial agent",
        default=lambda self: self.env.user.id,
    )
    date_start = fields.Date(
        string="Start date",
        default=lambda self: fields.Date.context_today(self),
    )
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
    invoicing_mode = fields.Selection(related="template_id.invoicing_mode")
    auto_create_payment = fields.Boolean(related="template_id.auto_create_payment")
    payment_token_id = fields.Many2one(
        comodel_name="payment.token",
        string="Payment Token",
        domain="[('partner_id', '=', partner_id)]",
        help="Saved payment method used to charge this subscription "
        "automatically when automatic payment is enabled.",
    )
    payment_exception = fields.Boolean(
        copy=False,
        help="Set when an automatic payment fails. The scheduled job skips "
        "subscriptions in this state until it is cleared, once the payment "
        "method has been fixed.",
        tracking=True,
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_payment_token(self):
        """Suggest the partner's most recent token without overriding a manual
        choice. Only relevant when the template enables automatic payment."""
        for record in self:
            if not record.auto_create_payment:
                continue
            if (
                record.payment_token_id
                and record.payment_token_id.partner_id.commercial_partner_id
                == record.partner_id.commercial_partner_id
            ):
                continue
            record.payment_token_id = (
                record.env["payment.token"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", record.partner_id.id),
                        ("company_id", "=", record.company_id.id),
                    ],
                    limit=1,
                    order="write_date desc",
                )
            )

    @api.constrains("payment_token_id", "partner_id")
    def _check_payment_token_partner(self):
        for record in self:
            if not record.payment_token_id:
                continue
            if (
                record.payment_token_id.partner_id.commercial_partner_id
                != record.partner_id.commercial_partner_id
            ):
                raise ValidationError(
                    self.env._(
                        "Payment token '%s' belongs to a different partner "
                        "and cannot be used for this subscription."
                    )
                    % record.payment_token_id.display_name
                )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        stage_ids = stages.search([], order=stages._order)
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
        for subscription in self.search([], order="recurring_next_date asc"):
            subscription = subscription.with_company(subscription.company_id)
            if subscription.in_progress:
                if (
                    subscription.recurring_next_date <= today
                    and subscription.sale_subscription_line_ids
                    and not subscription.payment_exception
                ):
                    try:
                        # Isolate each subscription so a failure (e.g. a
                        # rejected charge) rolls back only its own changes and
                        # never leaves a half-processed invoice behind for the
                        # rest of the batch.
                        with self.env.cr.savepoint():
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

    def _invoice_chatter_link(self, msg_static, invoice):
        return (
            f"<b>{msg_static}</b> "
            f"<a href=# data-oe-model=account.move data-oe-id={invoice.id}>"
            f"{invoice.display_name}</a>"
        )

    def _send_invoice_email(self, invoice):
        mail_template = self.template_id.invoice_mail_template_id
        self.env["account.move.send"]._generate_and_send_invoices(
            invoice, mail_template=mail_template, sending_methods=["email"]
        )

    def _get_or_create_draft_invoice(self):
        """Reuse a draft invoice left over from a previous failed automatic
        payment (so retries don't pile up duplicates), but never reuse one that
        already has an in-flight or successful transaction."""
        self.ensure_one()
        for invoice in self.invoice_ids.filtered(
            lambda m: m.state == "draft" and m.move_type == "out_invoice"
        ):
            if not invoice.transaction_ids.filtered(
                lambda t: t.state in ("pending", "authorized", "done")
            ):
                return invoice
        return self.create_invoice()

    def generate_invoice(self):
        invoice_number = ""
        message_body = ""
        msg_static = self.env._("Created invoice with reference")
        mode = self.template_id.invoicing_mode
        auto_pay = self.template_id.auto_create_payment
        payment_failed = False
        auto_pay_invoice = self.env["account.move"]

        if mode in ["draft", "invoice", "invoice_send"]:
            if auto_pay:
                # Charge before posting: the invoice is kept in draft and the
                # payment flow posts and reconciles it only on success, so a
                # failed charge never leaves a posted invoice owed or burns an
                # invoice number.
                invoice = self._get_or_create_draft_invoice()
                payment_failed = not self.create_payment(invoice)
                auto_pay_invoice = invoice
                if (
                    invoice.state == "posted"
                    and mode in ("invoice", "invoice_send")
                    and invoice.payment_state in ("in_payment", "paid")
                ):
                    self._send_invoice_email(invoice)
            else:
                invoice = self.create_invoice()
                if mode != "draft":
                    invoice.action_post()
                    self._send_invoice_email(invoice)
                    invoice_number = invoice.name
                    message_body = self._invoice_chatter_link(msg_static, invoice)

        if mode == "sale_and_invoice":
            order_id = self.create_sale_order()
            order_id.action_confirm()
            order_id.action_lock()
            new_invoice = order_id._create_invoices()
            new_invoice.invoice_origin = order_id.name + ", " + self.name
            if auto_pay:
                payment_failed = not self.create_payment(new_invoice)
                auto_pay_invoice = new_invoice
            else:
                new_invoice.action_post()
                if new_invoice.state == "posted":
                    invoice_number = new_invoice.name
                    message_body = self._invoice_chatter_link(msg_static, new_invoice)

        if auto_pay:
            # Automatic payment posts its own chatter, so skip the generic
            # "Created invoice" / "To validate" note:
            #  - a single "submitted; awaiting confirmation" note while the
            #    charge is still pending (the invoice stays draft),
            #  - a "confirmed" note with the real invoice number once the
            #    payment is captured (posted by the payment.transaction
            #    post-process hook), and
            #  - a failure note via _register_payment_failure.
            if not payment_failed and auto_pay_invoice.state != "posted":
                self.message_post(
                    body=self.env._(
                        "Automatic payment submitted; awaiting confirmation."
                    )
                )
        else:
            if not invoice_number:
                invoice_number = self.env._("To validate")
                message_body = f"<b>{msg_static}</b> {invoice_number}"
            self.message_post(body=Markup(message_body))

        # Keep the schedule on the failed period so the next run (once the
        # payment method is fixed) retries it instead of skipping ahead.
        if not payment_failed:
            self.calculate_recurring_next_date(self.recurring_next_date)

    def manual_invoice(self):
        invoice_id = self.create_invoice()
        self.calculate_recurring_next_date(self.recurring_next_date)
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

    def _payment_failure_activity_summary(self):
        return self.env._("Subscription automatic payment failed")

    def _register_payment_failure(self, message):
        """Flag the subscription, log a chatter note and schedule a to-do
        activity (visible in list and kanban) so the failure is surfaced and
        the scheduler stops retrying until it is resolved."""
        self.ensure_one()
        self.payment_exception = True
        self.message_post(body=message)
        summary = self._payment_failure_activity_summary()
        already_open = self.activity_ids.filtered(lambda a: a.summary == summary)
        if not already_open:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=summary,
                note=message,
                user_id=self.user_id.id or self.env.uid,
            )

    def _clear_payment_failure(self):
        """Clear the exception flag and resolve any open payment-failure
        activity once a charge succeeds or is accepted."""
        self.ensure_one()
        self.payment_exception = False
        summary = self._payment_failure_activity_summary()
        self.activity_ids.filtered(lambda a: a.summary == summary).unlink()

    def create_payment(self, invoice):
        """Charge ``invoice`` against the subscription's saved token using an
        offline (merchant-initiated) payment transaction.

        :return: ``True`` if the charge was captured or accepted for
            asynchronous capture (e.g. SEPA direct debit), ``False`` on a hard
            failure.
        """
        self.ensure_one()
        invoice.ensure_one()
        token = self.payment_token_id
        if not token:
            self._register_payment_failure(
                self.env._("No payment token found for partner %s")
                % invoice.partner_id.display_name
            )
            return False
        provider = token.provider_id
        if not provider.journal_id:
            self._register_payment_failure(
                self.env._("Payment provider %s has no payment journal configured.")
                % provider.display_name
            )
            return False
        payment_transaction = self.env["payment.transaction"].sudo()
        # The invoice is still in draft at charge time (charge-before-post), so
        # it has no sequence number yet (its name is empty or the "/"
        # placeholder). Fall back to the subscription's own reference for a
        # stable, traceable prefix instead of a timestamp.
        has_number = invoice.name and invoice.name != "/"
        reference = payment_transaction._compute_reference(
            provider.code, prefix=invoice.name if has_number else self.name
        )
        transaction = payment_transaction.create(
            {
                "provider_id": provider.id,
                "payment_method_id": token.payment_method_id.id,
                "token_id": token.id,
                "operation": "offline",
                "reference": reference,
                "amount": invoice.amount_total,
                "currency_id": invoice.currency_id.id,
                "partner_id": invoice.partner_id.id,
                "invoice_ids": [Command.set(invoice.ids)],
            }
        )
        try:
            transaction._send_payment_request()
        except Exception:
            logger.exception(
                "Automatic payment request failed for subscription %s", self.id
            )
            self._register_payment_failure(
                self.env._(
                    "The automatic payment request could not be sent. "
                    "Please check the payment method."
                )
            )
            return False
        if transaction.state == "done":
            # Skip the sale module's automatic invoice sending so this module
            # stays the single authority on when the (paid) invoice is emailed.
            transaction.with_context(skip_sale_auto_invoice_send=True)._post_process()
            self._clear_payment_failure()
            return True
        if transaction.state in ("pending", "authorized"):
            # Asynchronous capture: the charge has been submitted and the
            # provider will confirm it later via webhook. The chatter note is
            # posted by generate_invoice (and the confirmation note by the
            # payment.transaction post-process hook) to avoid duplicate
            # messages here.
            self._clear_payment_failure()
            return True
        self._register_payment_failure(
            self.env._("The automatic payment was declined (state: %s).")
            % transaction.state
        )
        return False
