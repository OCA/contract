# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_contract = fields.Boolean(
        string="Is a contract",
    )
    contract_id = fields.Many2one(
        comodel_name="contract.contract", string="Contract", copy=False
    )
    contract_template_id = fields.Many2one(
        comodel_name="contract.template",
        string="Contract Template",
        compute="_compute_contract_template_id",
    )
    recurring_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Invoice Every",
        copy=False,
    )
    recurring_invoicing_type = fields.Selection(
        [("pre-paid", "Pre-paid"), ("post-paid", "Post-paid")],
        default="pre-paid",
        string="Invoicing type",
        help="Specify if process date is 'from' or 'to' invoicing date",
        copy=False,
    )
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")

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

    @api.depends("product_id")
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

    @api.depends("product_id", "is_contract")
    def _compute_auto_renew(self):
        for rec in self:
            if rec.is_contract:
                rec.product_uom_qty = rec.product_id.default_qty
                rec.recurring_rule_type = rec.product_id.recurring_rule_type
                rec.recurring_invoicing_type = rec.product_id.recurring_invoicing_type
                rec.date_start = rec.date_start or fields.Date.today()

                rec.date_end = rec._get_date_end()
                rec.is_auto_renew = rec.product_id.is_auto_renew
                if rec.is_auto_renew:
                    rec.auto_renew_interval = rec.product_id.auto_renew_interval
                    rec.auto_renew_rule_type = rec.product_id.auto_renew_rule_type

    @api.onchange("date_start", "product_uom_qty", "recurring_rule_type", "is_contract")
    def onchange_date_start(self):
        for rec in self.filtered("is_contract"):
            rec.date_end = rec._get_date_end() if rec.date_start else False

    @api.onchange("product_id")
    def product_id_change(self):
        super().product_id_change()
        for rec in self:
            if rec.product_id.is_contract:
                rec.is_contract = True
            else:
                # Don't initialize wrong values
                rec.is_contract = False

    def _get_contract_line_qty(self):
        """Returns the quantity to be put on new contract lines."""
        self.ensure_one()
        # The quantity on the generated contract line is 1, as it
        # correspond to the most common use cases:
        # - quantity on the SO line = number of periods sold and unit
        #   price the price of one period, so the
        #   total amount of the SO corresponds to the planned value
        #   of the contract; in this case the quantity on the contract
        #   line must be 1
        # - quantity on the SO line = number of hours sold,
        #   automatic invoicing of the actual hours through a variable
        #   quantity formula, in which case the quantity on the contract
        #   line is not used
        # Other use cases are easy to implement by overriding this method.
        return 1.0

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
            "name": self.name,
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
            "analytic_account_id": self.order_id.analytic_account_id.id,
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

    @api.constrains("product_id", "contract_id")
    def _check_contract_sale_line_is_contract(self):
        for rec in self:
            if rec.is_contract and not rec.product_id.is_contract:
                raise ValidationError(
                    _(
                        'You can check the field "Is a contract" only for Contract product'
                    )
                )

    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        self.filtered("contract_id").update({"invoice_status": "no"})
        return res

    def invoice_line_create(self, invoice_id, qty):
        return super(
            SaleOrderLine, self.filtered(lambda l: not l.contract_id)
        ).invoice_line_create(invoice_id, qty)

    @api.depends(
        "qty_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "order_id.state",
        "is_contract",
    )
    def _get_to_invoice_qty(self):
        """
        sale line linked to contracts must not be invoiced from sale order
        """
        res = super()._get_to_invoice_qty()
        self.filtered("is_contract").update({"qty_to_invoice": 0.0})
        return res
