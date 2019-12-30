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
        comodel_name='contract.contract', string='Contract', copy=False
    )
    contract_template_id = fields.Many2one(
        comodel_name='contract.template',
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
        comodel_name="contract.line",
        string="Contract Line to replace",
        required=False,
        copy=False,
    )

    @api.multi
    def _get_auto_renew_rule_type(self):
        """monthly last day don't make sense for auto_renew_rule_type"""
        self.ensure_one()
        if self.recurring_rule_type == "monthlylastday":
            return "monthly"
        return self.recurring_rule_type

    @api.onchange('product_id')
    def onchange_product(self):
        contract_line_model = self.env['contract.line']
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
                    + contract_line_model.get_relative_delta(
                        rec._get_auto_renew_rule_type(),
                        int(rec.product_uom_qty),
                    )
                    - relativedelta(days=1)
                )

    @api.onchange('date_start', 'product_uom_qty', 'recurring_rule_type')
    def onchange_date_start(self):
        contract_line_model = self.env['contract.line']
        for rec in self.filtered('product_id.is_contract'):
            if not rec.date_start:
                rec.date_end = False
            else:
                rec.date_end = (
                    rec.date_start
                    + contract_line_model.get_relative_delta(
                        rec._get_auto_renew_rule_type(),
                        int(rec.product_uom_qty),
                    )
                    - relativedelta(days=1)
                )

    @api.multi
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
            'contract.line'
        ]._compute_first_recurring_next_date(
            self.date_start or fields.Date.today(),
            self.recurring_invoicing_type,
            self.recurring_rule_type,
            1,
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
            'auto_renew_rule_type': self._get_auto_renew_rule_type(),
            'termination_notice_interval': termination_notice_interval,
            'termination_notice_rule_type': termination_notice_rule_type,
            'contract_id': contract.id,
            'sale_order_line_id': self.id,
            'predecessor_contract_line_id': predecessor_contract_line_id,
            'analytic_account_id': self.order_id.analytic_account_id.id,
        }

    @api.multi
    def create_contract_line(self, contract):
        contract_line_model = self.env['contract.line']
        contract_line = self.env['contract.line']
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
                    rec.contract_line_id.stop(
                        rec.date_start - relativedelta(days=1)
                    )
                    predecessor_contract_line = rec.contract_line_id
            if predecessor_contract_line:
                new_contract_line = contract_line_model.create(
                    rec._prepare_contract_line_values(
                        contract, predecessor_contract_line.id
                    )
                )
                predecessor_contract_line.successor_contract_line_id = (
                    new_contract_line
                )
            else:
                new_contract_line = contract_line_model.create(
                    rec._prepare_contract_line_values(contract)
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
                    rec.contract_id.contract_template_id
                    and rec.contract_template_id
                    != rec.contract_id.contract_template_id
                ):
                    raise ValidationError(
                        _("Contract product has different contract template")
                    )

    def _compute_invoice_status(self):
        res = super(SaleOrderLine, self)._compute_invoice_status()
        for line in self.filtered('contract_id'):
            line.invoice_status = 'no'
        return res

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        return super(
            SaleOrderLine, self.filtered(lambda l: not l.contract_id)
        ).invoice_line_create(invoice_id, qty)

    @api.depends(
        'qty_invoiced',
        'qty_delivered',
        'product_uom_qty',
        'order_id.state',
        'product_id.is_contract',
    )
    def _get_to_invoice_qty(self):
        """
        sale line linked to contracts must not be invoiced from sale order
        """
        res = super()._get_to_invoice_qty()
        self.filtered('product_id.is_contract').update({'qty_to_invoice': 0.0})
        return res
