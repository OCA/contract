# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round


class ContractMakePlannedInvoice(models.TransientModel):
    _inherit = "contract.make.planned.invoice"

    active_installment_ids = fields.Many2many(
        comodel_name="contract.invoice.plan",
        compute="_compute_active_installment_ids",
    )
    next_bill_method = fields.Selection(
        selection=[
            ("auto", "Installment Sequence"),
            ("manual", "Manual Selection"),
        ],
        string="Next Bill By",
        default="auto",
        required=True,
    )
    installment_id = fields.Many2one(
        comodel_name="contract.invoice.plan",
        string="Invoice Plan",
        required=False,
        domain="[('id', 'in', active_installment_ids), ('installment', '>', 0)]",
        help="List only installment that has not been used in invoice",
    )
    apply_method_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Base On",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "contract.make.planned.invoice"),
        ],
        required=False,
        help="Choose the method to find matcing product line for this installment",
    )
    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        default=lambda self: self.env.context.get("active_id"),
    )
    contract_line_ids = fields.Many2many(
        comodel_name="contract.line",
        relation="select_invoice_plan_contract_line_rel",
        column1="wizard_id",
        column2="contract_line_id",
        string="Select Contract Line(s)",
        domain="[('contract_id', '=', contract_id)]",
        compute="_compute_contract_line_ids",
        store=True,
        readonly=False,
        help="List of product lines used to create invoice. Blank means all",
    )
    invoice_qty_line_ids = fields.One2many(
        comodel_name="select.contract.invoice.plan.qty",
        inverse_name="wizard_id",
        compute="_compute_invoice_qty_line_ids",
        store=True,
        readonly=False,
    )
    valid_amount = fields.Boolean(
        compute="_compute_valid_amount",
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        contract = self.env["contract.contract"].browse(
            self.env.context.get("active_ids", [])
        )
        res["next_bill_method"] = contract.next_bill_method or "auto"
        return res

    @api.depends("installment_id")
    def _compute_active_installment_ids(self):
        self.ensure_one()
        contract = self.env["contract.contract"].browse(
            self.env.context.get("active_ids", [])
        )
        # Get installment line without valid invoices created.
        installment_ids = []
        for installment in contract.invoice_plan_ids:
            states = installment.invoice_ids.mapped("state")
            if "draft" in states or "posted" in states:
                installment_ids.append(installment.id)
        self.active_installment_ids = self.env["contract.invoice.plan"].search(
            [
                ("contract_id", "=", contract.id),
                ("id", "not in", installment_ids),
                ("installment", ">", 0),
            ]
        )

    @api.depends("installment_id", "apply_method_id")
    def _compute_contract_line_ids(self):
        for rec in self:
            rec.contract_line_ids = False
            if rec.installment_id and rec.apply_method_id:
                ctx = {
                    "installment_id": rec.installment_id.id,
                    "contract_id": self.env.context.get("active_id"),
                }
                contract_line_ids = rec.apply_method_id.with_context(**ctx).run()
                if not contract_line_ids:
                    raise UserError(_("No product line with matched amount!"))
                rec.contract_line_ids = contract_line_ids  # [1,2,3,4]

    @api.depends("contract_line_ids")
    def _compute_invoice_qty_line_ids(self):
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Product Unit of Measure")
        for rec in self:
            rec.invoice_qty_line_ids = False
            expect_amount = rec.installment_id.amount
            contract_lines = rec.contract_line_ids
            lines_amount = sum(contract_lines.mapped("price_subtotal"))
            contract = contract_lines[:1].contract_id
            all_lines_amount = sum(contract.contract_line_ids.mapped("price_subtotal"))
            if rec.contract_line_ids and not lines_amount:
                raise UserError(_("Total contract amount must not be zero!"))
            for contract_line in rec.contract_line_ids:
                ratio = expect_amount / lines_amount
                ratio_all = expect_amount / all_lines_amount
                quantity = float_round(contract_line.quantity * ratio, prec)
                if not quantity:  # good for deposit case
                    quantity = -ratio_all
                if float_compare(quantity, contract_line.qty_to_invoice, 2) > 0:
                    quantity = contract_line.qty_to_invoice
                    amount = quantity * contract_line.price_unit
                    expect_amount -= amount
                    contract_lines -= contract_line
                    lines_amount = sum(contract_lines.mapped("price_subtotal"))
                line = self.env["select.contract.invoice.plan.qty"].new(
                    {"contract_line_id": contract_line._origin.id, "quantity": quantity}
                )
                rec.invoice_qty_line_ids += line

    @api.depends("invoice_qty_line_ids")
    def _compute_valid_amount(self):
        for rec in self:
            invoice_amount = sum(rec.invoice_qty_line_ids.mapped("amount"))
            installment = rec.installment_id.amount
            rec.valid_amount = float_compare(invoice_amount, installment, 2) == 0

    @api.onchange("installment_id")
    def _onchange_installment_id(self):
        if not self.installment_id:
            return
        min_installment = min(self.active_installment_ids.mapped("installment"))
        if self.installment_id.installment > min_installment:
            return {
                "warning": {
                    "title": _("Installment Warning:"),
                    "message": _(
                        "The next installment is 'Invoice Plan {}' "
                        "but you are choosing 'Invoice Plan {}'"
                    ).format(min_installment, self.installment_id.installment),
                }
            }

    def create_invoice_by_selection(self):
        contract = self.env["contract.contract"].browse(self._context.get("active_id"))
        contract.ensure_one()
        contract.sudo().with_context(
            next_bill_method=self.next_bill_method,
            invoice_plan_id=self.installment_id.id,
            invoice_qty_line_ids=[
                {
                    "contract_line_id": x.contract_line_id.id,
                    "quantity": x.quantity,
                }
                for x in self.invoice_qty_line_ids
            ],
        ).action_ip_create_invoice()
        contract.write({"next_bill_method": self.next_bill_method})
        return {"type": "ir.actions.act_window_close"}


class SelectContractInvoicePlanQty(models.TransientModel):
    _name = "select.contract.invoice.plan.qty"
    _description = "Compute quantity of each invoice lines, according to product lines"

    wizard_id = fields.Many2one(
        comodel_name="contract.make.planned.invoice",
        ondelete="cascade",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="wizard_id.contract_id.currency_id",
    )
    contract_id = fields.Many2one(
        related="wizard_id.contract_id",
    )
    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Product Line",
        required=True,
        domain="[('contract_id', '=', contract_id)]",
    )
    qty_not_invoiced = fields.Float(
        string="Not Accepted",
        related="contract_line_id.qty_to_invoice",
        digits="Product Unit of Measure",
    )
    quantity = fields.Float(
        string="To Invoice",
        digits="Product Unit of Measure",
    )
    amount = fields.Monetary(
        compute="_compute_amount",
        inverse="_inverse_amount",
    )
    _sql_constraints = [
        (
            "contract_line_unique",
            "unique(wizard_id, contract_line_id)",
            "You are selecting same product line more than one.",
        )
    ]

    @api.depends("quantity")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.quantity * rec.contract_line_id.price_unit

    @api.onchange("amount")
    def _inverse_amount(self):
        for rec in self:
            rec.quantity = rec.amount / rec.contract_line_id.price_unit
