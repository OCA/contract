# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContractTemplateLine(models.Model):
    _name = "contract.template.line"
    _inherit = "contract.recurring.mixin"
    _description = "Contract Template Line"
    _order = "sequence,id"

    sequence = fields.Integer(
        default=10,
        help="Defines line ordering in the contract.",
    )
    contract_id = fields.Many2one(
        comodel_name="contract.template",
        string="Contract",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        related="contract_id.company_id", store=True, readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", related="contract_id.partner_id"
    )
    # === Product & UOM ===
    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Text(
        string="Description",
        required=True,
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    quantity = fields.Float(default=1.0, required=True)
    product_uom_category_id = fields.Many2one(
        comodel_name="uom.category",
        related="product_id.uom_id.category_id",
        readonly=True,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        compute="_compute_uom_id",
        store=True,
        readonly=False,
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
    )

    # === Pricing ===

    automatic_price = fields.Boolean(
        string="Auto-price?",
        compute="_compute_automatic_price",
        store=True,
        readonly=False,
        help=(
            "If checked, the price will be taken from the pricelist. "
            "Otherwise, it must be set manually."
        ),
    )
    specific_price = fields.Float()
    price_unit = fields.Float(
        string="Unit Price",
        compute="_compute_price_unit",
        inverse="_inverse_price_unit",
    )
    currency_id = fields.Many2one(
        "res.currency"
    )  # Placeholder, overwritten in contract.line
    price_subtotal = fields.Monetary(
        string="Sub Total",
        compute="_compute_price_subtotal",
    )
    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        help="Discount to apply on generated invoices. Must be ≤ 100.",
    )

    # === Recurrence Configuration ===

    is_canceled = fields.Boolean(string="Canceled", default=False)

    # === Display / Notes ===

    display_type = fields.Selection(
        selection=[("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purposes.",
    )
    note_invoicing_mode = fields.Selection(
        selection=[
            ("with_previous_line", "With previous line"),
            ("with_next_line", "With next line"),
            ("custom", "Custom"),
        ],
        default="with_previous_line",
        help="When to invoice this note line relative to others.",
    )
    is_recurring_note = fields.Boolean(
        compute="_compute_is_recurring_note",
        string="Recurring Note",
    )

    # === Line-Level Recurrence Fields (computed from contract or local) ===

    recurring_rule_type = fields.Selection(
        compute="_compute_recurring_rule_type",
        store=True,
        readonly=False,
        required=True,
        copy=True,
    )
    recurring_invoicing_type = fields.Selection(
        compute="_compute_recurring_invoicing_type",
        store=True,
        readonly=False,
        required=True,
        copy=True,
    )
    recurring_interval = fields.Integer(
        compute="_compute_recurring_interval",
        store=True,
        readonly=False,
        required=True,
        copy=True,
    )
    date_start = fields.Date(
        compute="_compute_date_start",
        store=True,
        readonly=False,
        copy=True,
    )

    @api.depends("product_id")
    def _compute_name(self):
        for line in self:
            if line.product_id:
                partner = line.contract_id.partner_id or line.env.user.partner_id
                product = line.product_id.with_context(
                    lang=partner.lang,
                    partner=partner.id,
                )
                line.name = product.get_product_multiline_description_sale()

    @api.depends("product_id")
    def _compute_uom_id(self):
        for line in self:
            if not line.uom_id or (
                line.product_id.uom_id.category_id.id != line.uom_id.category_id.id
            ):
                line.uom_id = line.product_id.uom_id

    @api.depends("contract_id.contract_type")
    def _compute_automatic_price(self):
        """Reset automatic price if contract is switched to 'purchase'."""
        self.filtered(
            lambda line: line.contract_id.contract_type == "purchase"
            and line.automatic_price
        ).automatic_price = False

    @api.depends("display_type", "note_invoicing_mode")
    def _compute_is_recurring_note(self):
        for record in self:
            record.is_recurring_note = (
                record.display_type == "line_note"
                and record.note_invoicing_mode == "custom"
            )

    @api.depends(
        "automatic_price",
        "specific_price",
        "product_id",
        "quantity",
        "contract_id.pricelist_id",
        "contract_id.partner_id",
    )
    def _compute_price_unit(self):
        for line in self:
            if line.automatic_price and line.product_id:
                pricelist = (
                    line.contract_id.pricelist_id
                    or line.contract_id.partner_id.with_company(
                        line.contract_id.company_id
                    ).property_product_pricelist
                )
                product = line.product_id.with_context(
                    quantity=line.env.context.get("contract_line_qty", line.quantity),
                    pricelist=pricelist.id,
                    partner=line.contract_id.partner_id.id,
                    uom=line.uom_id.id,
                    date=line.env.context.get(
                        "old_date", fields.Date.context_today(line)
                    ),
                )
                line.price_unit = pricelist._get_product_price(product, quantity=1)
            else:
                line.price_unit = line.specific_price

    # Tip in https://github.com/odoo/odoo/issues/23891#issuecomment-376910788
    @api.onchange("price_unit")
    def _inverse_price_unit(self):
        for line in self.filtered(lambda x: not x.automatic_price):
            line.specific_price = line.price_unit

    @api.depends("quantity", "price_unit", "discount")
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            subtotal *= 1 - (line.discount / 100)
            cur = (
                line.contract_id.pricelist_id.currency_id
                if line.contract_id.pricelist_id
                else None
            )
            line.price_subtotal = cur.round(subtotal) if cur else subtotal

    # === Recurrence Field Synchronization ===

    def _set_recurrence_field(self, field):
        """Sync recurrence field from header or keep local depending on config."""
        for record in self:
            record[field] = (
                record[field]
                if record.contract_id.line_recurrence
                else record.contract_id[field]
            )

    @api.depends("contract_id.recurring_rule_type", "contract_id.line_recurrence")
    def _compute_recurring_rule_type(self):
        self._set_recurrence_field("recurring_rule_type")

    @api.depends("contract_id.recurring_invoicing_type", "contract_id.line_recurrence")
    def _compute_recurring_invoicing_type(self):
        self._set_recurrence_field("recurring_invoicing_type")

    @api.depends("contract_id.recurring_interval", "contract_id.line_recurrence")
    def _compute_recurring_interval(self):
        self._set_recurrence_field("recurring_interval")

    @api.depends("contract_id.date_start", "contract_id.line_recurrence")
    def _compute_date_start(self):
        self._set_recurrence_field("date_start")

    @api.depends("contract_id.line_recurrence")
    def _compute_recurring_next_date(self):
        res = super()._compute_recurring_next_date()
        self._set_recurrence_field("recurring_next_date")
        return res

    # === Constraints & Onchange ===

    @api.constrains("discount")
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(
                    self.env._("Discount should be less or equal to 100")
                )
