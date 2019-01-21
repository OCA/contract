# Copyright 2017 LasLabs Inc.
# Copyright 2017 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_contract = fields.Boolean(
        string='Is a contract', related="product_id.is_contract"
    )
    contract_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Contract', copy=False
    )
    contract_template_id = fields.Many2one(
        comodel_name='account.analytic.contract',
        string='Contract Template',
        related='product_id.product_tmpl_id.contract_template_id',
        readonly=True,
    )
    recurring_rule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('yearly', 'Year(s)'),
        ],
        default='monthly',
        string='Invoice Every',
        copy=False,
    )
    recurring_invoicing_type = fields.Selection(
        [('pre-paid', 'Pre-paid'), ('post-paid', 'Post-paid')],
        default='pre-paid',
        string='Invoicing type',
        help="Specify if process date is 'from' or 'to' invoicing date",
        copy=False,
    )
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    contract_line_id = fields.Many2one(
        comodel_name="account.analytic.invoice.line",
        string="Contract Line to replace",
        required=False,
        copy=False,
    )

    @api.onchange('product_id')
    def onchange_product(self):
        contract_line_env = self.env['account.analytic.invoice.line']
        for rec in self:
            if rec.product_id.is_contract:
                rec.product_uom_qty = rec.product_id.default_qty
                rec.recurring_rule_type = rec.product_id.recurring_rule_type
                rec.recurring_invoicing_type = (
                    rec.product_id.recurring_invoicing_type
                )
                rec.date_start = rec.date_start or fields.Date.today()
                rec.date_end = (
                    rec.date_start
                    + contract_line_env.get_relative_delta(
                        rec.product_id.recurring_rule_type,
                        int(rec.product_uom_qty),
                    )
                    - relativedelta(days=1)
                )

    @api.onchange('date_start', 'product_uom_qty', 'recurring_rule_type')
    def onchange_date_start(self):
        for rec in self:
            if not rec.date_start:
                rec.date_end = False
            else:
                rec.date_end = (
                    rec.date_start
                    + self.env[
                        'account.analytic.invoice.line'
                    ].get_relative_delta(
                        rec.recurring_rule_type, int(rec.product_uom_qty)
                    )
                    - relativedelta(days=1)
                )

    @api.multi
    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line
    ):
        self.ensure_one()
        recurring_next_date = self.env[
            'account.analytic.invoice.line'
        ]._compute_first_recurring_next_date(
            self.date_start or fields.Date.today(),
            self.recurring_invoicing_type,
            self.recurring_rule_type,
            int(self.product_uom_qty),
        )
        termination_notice_interval = (
            self.product_id.termination_notice_interval
        )
        termination_notice_rule_type = (
            self.product_id.termination_notice_rule_type
        )
        return {
            'sequence': self.sequence,
            'product_id': self.product_id.id,
            'name': self.name,
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
            'quantity': 1.0,
            'uom_id': self.product_uom.id,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'date_end': self.date_end,
            'date_start': self.date_start or fields.Date.today(),
            'recurring_next_date': recurring_next_date,
            'recurring_interval': 1,
            'recurring_invoicing_type': self.recurring_invoicing_type,
            'recurring_rule_type': self.recurring_rule_type,
            'is_auto_renew': self.product_id.is_auto_renew,
            'auto_renew_interval': self.product_uom_qty,
            'auto_renew_rule_type': self.product_id.recurring_rule_type,
            'termination_notice_interval': termination_notice_interval,
            'termination_notice_rule_type': termination_notice_rule_type,
            'contract_id': contract.id,
            'sale_order_line_id': self.id,
            'predecessor_contract_line_id': predecessor_contract_line.id,
        }

    @api.multi
    def create_contract_line(self, contract):
        contract_line_env = self.env['account.analytic.invoice.line']
        contract_line = self.env['account.analytic.invoice.line']
        for rec in self:
            if rec.contract_line_id:
                rec.contract_line_id.stop(
                    rec.date_start - relativedelta(days=1)
                )
            new_contract_line = contract_line_env.create(
                rec._prepare_contract_line_values(
                    contract, rec.contract_line_id
                )
            )
            if rec.contract_line_id:
                rec.contract_line_id.successor_contract_line_id = (
                    new_contract_line
                )
            contract_line |= new_contract_line
        return contract_line

    @api.constrains('contract_id')
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

    @api.constrains('product_id', 'contract_id')
    def _check_contract_sale_contract_template(self):
        for rec in self:
            if rec.contract_id:
                if (
                    rec.contract_template_id
                    != rec.contract_id.contract_template_id
                ):
                    raise ValidationError(
                        _("Contract product has different contract template")
                    )

    def _compute_invoice_status(self):
        super(SaleOrderLine, self)._compute_invoice_status()
        for line in self.filtered('contract_id'):
            line.invoice_status = 'no'

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        return super(
            SaleOrderLine, self.filtered(lambda l: not l.contract_id)
        ).invoice_line_create(invoice_id, qty)
