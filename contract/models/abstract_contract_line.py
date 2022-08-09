# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ContractAbstractContractLine(models.AbstractModel):
    _inherit = "contract.recurrency.basic.mixin"
    _name = "contract.abstract.contract.line"
    _description = "Abstract Recurring Contract Line"

    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Text(string="Description", required=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner", related="contract_id.partner_id"
    )
    quantity = fields.Float(default=1.0, required=True)
    allowed_uom_categ_id = fields.Many2one(related="product_id.uom_id.category_id")
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=?', allowed_uom_categ_id)]",
    )
    automatic_price = fields.Boolean(
        string="Auto-price?",
        help="If this is marked, the price will be obtained automatically "
        "applying the pricelist to the product. If not, you will be "
        "able to introduce a manual price",
    )
    specific_price = fields.Float(string="Specific Price")
    price_unit = fields.Float(
        string="Unit Price",
        compute="_compute_price_unit",
        inverse="_inverse_price_unit",
    )
    price_subtotal = fields.Float(
        compute="_compute_price_subtotal",
        digits="Account",
        string="Sub Total",
    )
    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        help="Discount that is applied in generated invoices."
        " It should be less or equal to 100",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Sequence of the contract line when displaying contracts",
    )
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
    last_date_invoiced = fields.Date(string="Last Date Invoiced")
    is_canceled = fields.Boolean(string="Canceled", default=False)
    is_auto_renew = fields.Boolean(string="Auto Renew", default=False)
    auto_renew_interval = fields.Integer(
        default=1,
        string="Renew Every",
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
        string="Renewal type",
        help="Specify Interval for automatic renewal.",
    )
    termination_notice_interval = fields.Integer(
        default=1, string="Termination Notice Before"
    )
    termination_notice_rule_type = fields.Selection(
        [("daily", "Day(s)"), ("weekly", "Week(s)"), ("monthly", "Month(s)")],
        default="monthly",
        string="Termination Notice type",
    )
    contract_id = fields.Many2one(
        string="Contract",
        comodel_name="contract.abstract.contract",
        required=True,
        ondelete="cascade",
    )
    display_type = fields.Selection(
        selection=[("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )
    note_invoicing_mode = fields.Selection(
        selection=[
            ("with_previous_line", "With previous line"),
            ("with_next_line", "With next line"),
            ("custom", "Custom"),
        ],
        default="with_previous_line",
        help="Defines when the Note is invoiced:\n"
        "- With previous line: If the previous line can be invoiced.\n"
        "- With next line: If the next line can be invoiced.\n"
        "- Custom: Depending on the recurrence to be define.",
    )
    is_recurring_note = fields.Boolean(compute="_compute_is_recurring_note")
    company_id = fields.Many2one(related="contract_id.company_id", store=True)

    def _set_recurrence_field(self, field):
        """Helper method for computed methods that gets the equivalent field
        in the header.

        We need to re-assign the original value for avoiding a missing error.
        """
        for record in self:
            if record.contract_id.line_recurrence:
                record[field] = record[field]
            else:
                record[field] = record.contract_id[field]

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

    @api.depends("contract_id.recurring_next_date", "contract_id.line_recurrence")
    def _compute_recurring_next_date(self):
        super()._compute_recurring_next_date()
        self._set_recurrence_field("recurring_next_date")

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
        "uom_id",
    )
    def _compute_price_unit(self):
        """Get the specific price if no auto-price, and the price obtained
        from the pricelist otherwise.
        """
        for line in self:
            if line.automatic_price:
                pricelist = (
                    line.contract_id.pricelist_id
                    or line.contract_id.partner_id.with_company(
                        line.contract_id.company_id
                    ).property_product_pricelist
                )
                product = line.product_id.with_context(
                    quantity=line.env.context.get(
                        "contract_line_qty",
                        line.quantity,
                    ),
                    pricelist=pricelist.id,
                    partner=line.contract_id.partner_id,
                    date=line.env.context.get(
                        "old_date", fields.Date.context_today(line)
                    ),
                    uom=line.uom_id.id,
                )
                line.price_unit = product.price
            else:
                line.price_unit = line.specific_price

    # Tip in https://github.com/odoo/odoo/issues/23891#issuecomment-376910788
    @api.onchange("price_unit")
    def _inverse_price_unit(self):
        """Store the specific price in the no auto-price records."""
        for line in self.filtered(lambda x: not x.automatic_price):
            line.specific_price = line.price_unit

    @api.depends("quantity", "price_unit", "discount")
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            if line.contract_id.pricelist_id:
                cur = line.contract_id.pricelist_id.currency_id
                line.price_subtotal = cur.round(subtotal)
            else:
                line.price_subtotal = subtotal

    @api.constrains("discount")
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(_("Discount should be less or equal to 100"))

    @api.onchange("product_id")
    def _onchange_product_id(self):
        vals = {}
        if not self.uom_id or (
            self.product_id.uom_id.category_id.id != self.uom_id.category_id.id
        ):
            vals["uom_id"] = self.product_id.uom_id

        date = self.recurring_next_date or fields.Date.context_today(self)
        partner = self.contract_id.partner_id or self.env.user.partner_id
        product = self.product_id.with_context(
            lang=partner.lang,
            partner=partner.id,
            quantity=self.quantity,
            date=date,
            pricelist=self.contract_id.pricelist_id.id,
            uom=self.uom_id.id,
        )
        vals["name"] = self.product_id.get_product_multiline_description_sale()
        vals["price_unit"] = product.price
        self.update(vals)
