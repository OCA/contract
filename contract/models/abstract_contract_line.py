# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ContractAbstractContractLine(models.AbstractModel):
    _name = 'contract.abstract.contract.line'
    _description = 'Abstract Recurring Contract Line'

    product_id = fields.Many2one(
        'product.product', string='Product'
    )

    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(default=1.0, required=True)
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure'
    )
    automatic_price = fields.Boolean(
        string="Auto-price?",
        help="If this is marked, the price will be obtained automatically "
        "applying the pricelist to the product. If not, you will be "
        "able to introduce a manual price",
    )
    specific_price = fields.Float(string='Specific Price')
    price_unit = fields.Float(
        string='Unit Price',
        compute="_compute_price_unit",
        inverse="_inverse_price_unit",
    )
    price_subtotal = fields.Float(
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'),
        string='Sub Total',
    )
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        help='Discount that is applied in generated invoices.'
        ' It should be less or equal to 100',
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Sequence of the contract line when displaying contracts",
    )
    recurring_rule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('quarterly', 'Quarter(s)'),
            ('semesterly', 'Semester(s)'),
            ('yearly', 'Year(s)'),
        ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic invoice generation.",
        required=True,
    )
    recurring_invoicing_type = fields.Selection(
        [('pre-paid', 'Pre-paid'), ('post-paid', 'Post-paid')],
        default='pre-paid',
        string='Invoicing type',
        help=(
            "Specify if the invoice must be generated at the beginning "
            "(pre-paid) or end (post-paid) of the period."
        ),
        required=True,
    )
    recurring_invoicing_offset = fields.Integer(
        compute="_compute_recurring_invoicing_offset",
        string="Invoicing offset",
        help=(
            "Number of days to offset the invoice from the period end "
            "date (in post-paid mode) or start date (in pre-paid mode)."
        )
    )
    recurring_interval = fields.Integer(
        default=1,
        string='Invoice Every',
        help="Invoice every (Days/Week/Month/Year)",
        required=True,
    )
    date_start = fields.Date(string='Date Start')
    recurring_next_date = fields.Date(string='Date of Next Invoice')
    last_date_invoiced = fields.Date(string='Last Date Invoiced')
    is_canceled = fields.Boolean(string="Canceled", default=False)
    is_auto_renew = fields.Boolean(string="Auto Renew", default=False)
    auto_renew_interval = fields.Integer(
        default=1,
        string='Renew Every',
        help="Renew every (Days/Week/Month/Year)",
    )
    auto_renew_rule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)'),
        ],
        default='yearly',
        string='Renewal type',
        help="Specify Interval for automatic renewal.",
    )
    termination_notice_interval = fields.Integer(
        default=1, string='Termination Notice Before'
    )
    termination_notice_rule_type = fields.Selection(
        [('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)')],
        default='monthly',
        string='Termination Notice type',
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='contract.abstract.contract',
        required=True,
        ondelete='cascade',
    )
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False,
        help="Technical field for UX purpose."
    )
    note_invoicing_mode = fields.Selection(
        selection=[
            ('with_previous_line', 'With previous line'),
            ('with_next_line', 'With next line'),
            ('custom', 'Custom'),
        ],
        default='with_previous_line',
        help="Defines when the Note is invoiced:\n"
             "- With previous line: If the previous line can be invoiced.\n"
             "- With next line: If the next line can be invoiced.\n"
             "- Custom: Depending on the recurrence to be define."
    )
    is_recurring_note = fields.Boolean(compute="_compute_is_recurring_note")

    @api.model
    def _get_default_recurring_invoicing_offset(
        self, recurring_invoicing_type, recurring_rule_type
    ):
        if (
            recurring_invoicing_type == 'pre-paid'
            or recurring_rule_type == 'monthlylastday'
        ):
            return 0
        else:
            return 1

    def is_recurring_note(self):
        for record in self:
            record.is_recurring_note = (
                record.display_type == 'line_note'
                and record.note_invoicing_mode == 'custom'
            )

    @api.depends('recurring_invoicing_type', 'recurring_rule_type')
    def _compute_recurring_invoicing_offset(self):
        for rec in self:
            rec.recurring_invoicing_offset = (
                self._get_default_recurring_invoicing_offset(
                    rec.recurring_invoicing_type, rec.recurring_rule_type
                )
            )

    @api.depends(
        'automatic_price',
        'specific_price',
        'product_id',
        'quantity',
        'contract_id.pricelist_id',
        'contract_id.partner_id',
    )
    def _compute_price_unit(self):
        """Get the specific price if no auto-price, and the price obtained
        from the pricelist otherwise.
        """
        for line in self:
            if line.automatic_price:
                pricelist = (
                    line.contract_id.pricelist_id or
                    line.contract_id.partner_id.with_context(
                        force_company=line.contract_id.company_id.id,
                    ).property_product_pricelist
                )
                product = line.product_id.with_context(
                    quantity=line.env.context.get(
                        'contract_line_qty',
                        line.quantity,
                    ),
                    pricelist=pricelist.id,
                    partner=line.contract_id.partner_id.id,
                    date=line.env.context.get(
                        'old_date', fields.Date.context_today(line)
                    ),
                )
                line.price_unit = product.price
            else:
                line.price_unit = line.specific_price

    # Tip in https://github.com/odoo/odoo/issues/23891#issuecomment-376910788
    @api.onchange('price_unit')
    def _inverse_price_unit(self):
        """Store the specific price in the no auto-price records."""
        for line in self.filtered(lambda x: not x.automatic_price):
            line.specific_price = line.price_unit

    @api.multi
    @api.depends('quantity', 'price_unit', 'discount')
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

    @api.multi
    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(
                    _("Discount should be less or equal to 100")
                )

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'uom_id': []}}

        vals = {}
        domain = {
            'uom_id': [
                ('category_id', '=', self.product_id.uom_id.category_id.id)
            ]
        }
        if not self.uom_id or (
            self.product_id.uom_id.category_id.id != self.uom_id.category_id.id
        ):
            vals['uom_id'] = self.product_id.uom_id

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
        vals['name'] = self.product_id.get_product_multiline_description_sale()
        vals['price_unit'] = product.price
        self.update(vals)
        return {'domain': domain}
