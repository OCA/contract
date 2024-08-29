# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MONTH_NB_MAPPING = {
    "monthly": 1,
    "quarterly": 3,
    "semesterly": 6,
    "yearly": 12,
}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_contract = fields.Boolean(
        string="Is a contract", related="product_id.is_contract"
    )
    contract_id = fields.Many2one(
        comodel_name="contract.contract", string="Contract", copy=False
    )
    contract_template_id = fields.Many2one(
        comodel_name="contract.template",
        string="Contract Template",
        compute="_compute_contract_template_id",
    )
    recurring_rule_type = fields.Selection(related="product_id.recurring_rule_type")
    recurring_invoicing_type = fields.Selection(
        related="product_id.recurring_invoicing_type"
    )
    date_start = fields.Date()
    date_end = fields.Date()

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line to replace",
        required=False,
        copy=False,
    )
    is_auto_renew = fields.Boolean(
        string="Auto Renew",
        compute="_compute_auto_renew",
        default=False,
        store=True,
        readonly=False,
    )
    auto_renew_interval = fields.Integer(
        default=1,
        string="Renew Every",
        compute="_compute_auto_renew",
        store=True,
        readonly=False,
        help="Renew every (Days/Week/Month/Year)",
    )
    auto_renew_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("yearly", "Year(s)"),
        ],
        default="yearly",
        compute="_compute_auto_renew",
        store=True,
        readonly=False,
        string="Renewal type",
        help="Specify Interval for automatic renewal.",
    )
    contract_start_date_method = fields.Selection(
        related="product_id.contract_start_date_method"
    )

    @api.constrains("contract_id")
    def _check_contact_is_not_terminated(self):
        for rec in self:
            if (
                rec.order_id.state not in ("sale", "done", "cancel")
                and rec.contract_id.is_terminated
            ):
                raise ValidationError(
                    _("You can't upsell or downsell a terminated contract")
                )

    @api.depends("product_id", "order_id.company_id")
    def _compute_contract_template_id(self):
        for rec in self:
            rec.contract_template_id = rec.product_id.with_company(
                rec.order_id.company_id
            ).property_contract_template_id

    def _get_auto_renew_rule_type(self):
        """monthly last day don't make sense for auto_renew_rule_type"""
        self.ensure_one()
        if self.recurring_rule_type == "monthlylastday":
            return "monthly"
        return self.recurring_rule_type

    def _get_date_end(self):
        self.ensure_one()
        contract_start_date_method = self.product_id.contract_start_date_method
        date_end = False
        if contract_start_date_method == "manual":
            contract_line_model = self.env["contract.line"]
            date_end = (
                self.date_start
                + contract_line_model.get_relative_delta(
                    self._get_auto_renew_rule_type(),
                    int(self.product_uom_qty),
                )
                - relativedelta(days=1)
            )
        return date_end

    @api.depends("product_id")
    def _compute_auto_renew(self):
        for rec in self:
            if rec.product_id.is_contract:
                rec.product_uom_qty = rec.product_id.default_qty
                contract_start_date_method = rec.product_id.contract_start_date_method
                if contract_start_date_method == "manual":
                    rec.date_start = rec.date_start or fields.Date.today()
                rec.date_end = rec._get_date_end()
                rec.is_auto_renew = rec.product_id.is_auto_renew
                if rec.is_auto_renew:
                    rec.auto_renew_interval = rec.product_id.auto_renew_interval
                    rec.auto_renew_rule_type = rec.product_id.auto_renew_rule_type

    @api.onchange("date_start", "product_uom_qty")
    def onchange_date_start(self):
        for rec in self.filtered("product_id.is_contract"):
            rec.date_end = rec._get_date_end() if rec.date_start else False

    def _get_contract_line_qty(self):
        """Returns the amount that will be placed in new contract lines."""
        self.ensure_one()
        # The quantity in the generated contract line is the quantity of
        # product requested in the order, since they correspond to the most common
        # use cases.
        # Other use cases are easy to implement by overriding this method.
        return self.product_uom_qty

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        """
        :param contract: related contract
        :param predecessor_contract_line_id: contract line to replace id
        :return: new contract line dict
        """
        self.ensure_one()
        recurring_next_date = self.env[
            "contract.line"
        ]._compute_first_recurring_next_date(
            self.date_start or fields.Date.today(),
            self.recurring_invoicing_type,
            self.recurring_rule_type,
            1,
        )
        termination_notice_interval = self.product_id.termination_notice_interval
        termination_notice_rule_type = self.product_id.termination_notice_rule_type
        return {
            "sequence": self.sequence,
            "product_id": self.product_id.id,
            "name": self.name.split(":\n")[0],
            "quantity": self._get_contract_line_qty(),
            "uom_id": self.product_uom.id,
            "price_unit": self.price_unit,
            "discount": self.discount,
            "date_end": self.date_end,
            "date_start": self.date_start or fields.Date.today(),
            "recurring_next_date": recurring_next_date,
            "recurring_interval": 1,
            "recurring_invoicing_type": self.recurring_invoicing_type,
            "recurring_rule_type": self.recurring_rule_type,
            "is_auto_renew": self.is_auto_renew,
            "auto_renew_interval": self.auto_renew_interval,
            "auto_renew_rule_type": self.auto_renew_rule_type,
            "termination_notice_interval": termination_notice_interval,
            "termination_notice_rule_type": termination_notice_rule_type,
            "contract_id": contract.id,
            "sale_order_line_id": self.id,
            "predecessor_contract_line_id": predecessor_contract_line_id,
            "analytic_distribution": self.analytic_distribution,
        }

    def create_contract_line(self, contract):
        contract_line_model = self.env["contract.line"]
        contract_line = self.env["contract.line"]
        predecessor_contract_line = False
        for rec in self:
            if rec.contract_line_id:
                # If the upsell/downsell line start at the same date or before
                # the contract line to replace supposed to start, we cancel
                # the one to be replaced. Otherwise we stop it.
                if rec.date_start <= rec.contract_line_id.date_start:
                    # The contract will handel the contract line integrity
                    # An exception will be raised if we try to cancel an
                    # invoiced contract line
                    rec.contract_line_id.cancel()
                elif (
                    not rec.contract_line_id.date_end
                    or rec.date_start <= rec.contract_line_id.date_end
                ):
                    rec.contract_line_id.stop(rec.date_start - relativedelta(days=1))
                    predecessor_contract_line = rec.contract_line_id
            if predecessor_contract_line:
                new_contract_line = contract_line_model.create(
                    rec._prepare_contract_line_values(
                        contract, predecessor_contract_line.id
                    )
                )
                predecessor_contract_line.successor_contract_line_id = new_contract_line
            else:
                new_contract_line = contract_line_model.create(
                    rec._prepare_contract_line_values(contract)
                )
            contract_line |= new_contract_line
        return contract_line

    @api.constrains("contract_id")
    def _check_contract_sale_partner(self):
        for rec in self:
            if rec.contract_id:
                if rec.order_id.partner_id != rec.contract_id.partner_id:
                    raise ValidationError(
                        _(
                            "Sale Order and contract should be "
                            "linked to the same partner"
                        )
                    )

    @api.constrains("product_id", "contract_id")
    def _check_contract_sale_contract_template(self):
        for rec in self:
            if rec.contract_id:
                if (
                    rec.contract_id.contract_template_id
                    and rec.contract_template_id != rec.contract_id.contract_template_id
                ):
                    raise ValidationError(
                        _("Contract product has different contract template")
                    )

    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        self.filtered("contract_id").update({"invoice_status": "no"})
        return res

    def invoice_line_create(self, invoice_id, qty):
        return super(
            SaleOrderLine, self.filtered(lambda line: not line.contract_id)
        ).invoice_line_create(invoice_id, qty)

    @api.depends("qty_invoiced", "qty_delivered", "product_uom_qty", "state")
    def _compute_qty_to_invoice(self):
        """
        sale line linked to contracts must not be invoiced from sale order
        """
        res = super()._compute_qty_to_invoice()
        self.filtered("product_id.is_contract").update({"qty_to_invoice": 0.0})
        return res

    def _set_contract_line_start_date(self):
        """Set date start of lines using it's method and the confirmation date."""
        for line in self:
            if (
                line.contract_start_date_method == "manual"
                or line.recurring_rule_type in ["daily", "weekly", "monthlylastday"]
            ):
                continue
            is_end = "end_" in line.contract_start_date_method
            today = fields.Date.today()
            month_period = month = today.month
            month_nb = MONTH_NB_MAPPING[line.recurring_rule_type]
            # The period number is started by 0 to be able to calculate the month
            period_number = (month - 1) // month_nb
            if line.recurring_rule_type == "yearly":
                month_period = 1
            elif line.recurring_rule_type != "monthly":
                # Checking quarterly and semesterly
                month_period = period_number * month_nb + 1
            forced_month = 0
            if line.recurring_rule_type != "monthly":
                forced_value = int(
                    line.product_id["force_month_%s" % line.recurring_rule_type]
                )
                if forced_value:
                    # When the selected period is yearly, the period_number field is
                    # 0, so forced_month will take the value of the forced month set
                    # on product.
                    forced_month = month_nb * period_number + forced_value
            # If forced_month is set, use it, but if it isn't use the month_period
            start_date = today + relativedelta(
                day=1, month=forced_month or month_period
            )
            if is_end:
                increment = month_nb - 1 if not forced_month else 0
                start_date = start_date + relativedelta(months=increment, day=31)
            if "_next" in line.contract_start_date_method and start_date <= today:
                start_date = start_date + relativedelta(months=month_nb)
                if is_end:
                    start_date = start_date + relativedelta(day=31)
            line.date_start = start_date

    @api.depends("product_id")
    def _compute_name(self):
        res = super()._compute_name()
        for line in self:
            if line.is_contract:
                date_text = ""
                if line.contract_start_date_method == "manual":
                    date_text = "%s" % line.date_start
                    if line.date_end:
                        date_text += " -> %s" % line.date_end
                else:
                    field_info = dict(
                        line._fields["contract_start_date_method"].get_description(
                            self.env
                        )
                    )
                    field_selection = dict(field_info.get("selection"))
                    start_method_label = field_selection.get(
                        line.contract_start_date_method
                    )
                    date_text = "%s" % start_method_label
                    if (
                        line.recurring_rule_type != "monthly"
                        and line.product_id["force_month_%s" % line.recurring_rule_type]
                    ):
                        field_info = dict(
                            self.env["product.template"]
                            ._fields["force_month_%s" % line.recurring_rule_type]
                            .get_description(self.env)
                        )
                        field_selection = dict(field_info.get("selection"))
                        force_month_label = field_selection.get(
                            line.product_id["force_month_%s" % line.recurring_rule_type]
                        )
                        date_text += " (%s)" % force_month_label
                field_info = dict(
                    self._fields["recurring_rule_type"].get_description(self.env)
                )
                field_selection = dict(field_info.get("selection"))
                recurring_rule_label = field_selection.get(line.recurring_rule_type)
                field_info = dict(
                    self._fields["recurring_invoicing_type"].get_description(self.env)
                )
                field_selection = dict(field_info.get("selection"))
                invoicing_type_label = field_selection.get(
                    line.recurring_invoicing_type
                )
                line.name = _(
                    """{product}:
    - Recurrency: {recurring_rule}
    - Invoicing Type: {invoicing_type}
    - Date: {date_text}
                """
                ).format(
                    product=line.product_id.display_name,
                    recurring_rule=recurring_rule_label,
                    invoicing_type=invoicing_type_label,
                    date_text=date_text,
                )

        return res
