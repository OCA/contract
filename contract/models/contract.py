# -*- coding: utf-8 -*-
# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
import logging

from openerp import _, api, fields, models
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountAnalyticInvoiceLine(models.Model):
    _name = 'account.analytic.invoice.line'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(default=1.0, required=True)
    uom_id = fields.Many2one(
        'product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float('Unit Price', required=True)
    price_subtotal = fields.Float(
        compute='_compute_price_subtotal',
        digits_compute=dp.get_precision('Account'),
        string='Sub Total')
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        help='Discount that is applied in generated invoices.'
             ' It should be less or equal to 100')

    @api.multi
    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            if line.analytic_account_id.pricelist_id:
                cur = line.analytic_account_id.pricelist_id.currency_id
                line.price_subtotal = cur.round(subtotal)
            else:
                line.price_subtotal = subtotal

    @api.multi
    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(
                    _("Discount should be less or equal to 100"))

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'uom_id': []}}

        vals = {}
        domain = {'uom_id': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.uom_id or (self.product_id.uom_id.category_id.id !=
                               self.uom_id.category_id.id):
            vals['uom_id'] = self.product_id.uom_id

        product = self.product_id.with_context(
            lang=self.analytic_account_id.partner_id.lang,
            partner=self.analytic_account_id.partner_id.id,
            quantity=self.quantity,
            date=self.analytic_account_id.recurring_next_date,
            pricelist=self.analytic_account_id.pricelist_id.id,
            uom=self.uom_id.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        vals['price_unit'] = product.price
        self.update(vals)
        return {'domain': domain}


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _default_journal(self):
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist')
    date_start = fields.Date(default=fields.Date.context_today)
    recurring_invoice_line_ids = fields.One2many(
        comodel_name='account.analytic.invoice.line',
        inverse_name='analytic_account_id',
        copy=True,
        string='Invoice Lines')
    recurring_invoices = fields.Boolean(
        string='Generate recurring invoices automatically')
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrency',
        help="Specify Interval for automatic invoice generation.")
    recurring_invoicing_type = fields.Selection(
        [('pre-paid', 'Pre-paid'),
         ('post-paid', 'Post-paid'),
         ],
        default='pre-paid',
        string='Invoicing type',
        help="Specify if process date is 'from' or 'to' invoicing date")
    recurring_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)")
    recurring_next_date = fields.Date(
        default=fields.Date.context_today,
        copy=False,
        string='Date of Next Invoice')
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=_default_journal,
        domain="[('type', '=', 'sale'),('company_id', '=', company_id)]")
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.onchange('recurring_invoices')
    def _onchange_recurring_invoices(self):
        if self.date_start and self.recurring_invoices:
            self.recurring_next_date = self.date_start

    @api.model
    def get_relalive_delta(self, recurring_rule_type, interval):
        if recurring_rule_type == 'daily':
            return relativedelta(days=interval)
        elif recurring_rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif recurring_rule_type == 'monthly':
            return relativedelta(months=interval)
        elif recurring_rule_type == 'monthlylastday':
            return relativedelta(months=interval, day=31)
        else:
            return relativedelta(years=interval)

    @api.model
    def _insert_markers(self, line, date_start, next_date, date_format):
        contract = line.analytic_account_id
        if contract.recurring_invoicing_type == 'pre-paid':
            date_from = date_start
            date_to = next_date - relativedelta(days=1)
        else:
            date_from = (date_start -
                         self.get_relalive_delta(contract.recurring_rule_type,
                                                 contract.recurring_interval) +
                         relativedelta(days=1))
            date_to = date_start
        name = line.name
        name = name.replace('#START#', date_from.strftime(date_format))
        name = name.replace('#END#', date_to.strftime(date_format))
        return name

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id,
            'discount': line.discount,
        })
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        # Insert markers
        name = line.name
        contract = line.analytic_account_id
        if 'old_date' in self.env.context and 'next_date' in self.env.context:
            lang_obj = self.env['res.lang']
            lang = lang_obj.search(
                [('code', '=', contract.partner_id.lang)])
            date_format = lang.date_format or '%m/%d/%Y'
            name = self._insert_markers(
                line, self.env.context['old_date'],
                self.env.context['next_date'], date_format)
        invoice_line_vals.update({
            'name': name,
            'account_analytic_id': contract.id,
            'price_unit': line.price_unit,
        })
        return invoice_line_vals

    @api.multi
    def _prepare_invoice(self):
        """Prepare the values for the invoice creation from the contract(s)
        given. It's possible to provide several contracts. Only one invoice
        will be created and most of the values will be taken from first
        contract, but there are certain values that can be obtained from all
        of them (for example, the origin field).

        :param self: Recordset of contract(s).
        :returns: Values for invoice creation.
        :rtype: dict
        """
        contract = self[:1]
        if not contract.partner_id:
            raise ValidationError(
                _("You must first select a Customer for Contract %s!") %
                contract.name)
        journal = contract.journal_id or self.env['account.journal'].search(
            [('type', '=', 'sale'),
             ('company_id', '=', contract.company_id.id)],
            limit=1)
        if not journal:
            raise ValidationError(
                _("Please define a sale journal for the company '%s'.") %
                (contract.company_id.name or '',))
        currency = (
            contract.pricelist_id.currency_id or
            contract.partner_id.property_product_pricelist.currency_id or
            contract.company_id.currency_id
        )
        invoice = self.env['account.invoice'].new({
            'reference': ', '.join(self.filtered('code').mapped('code')),
            'type': 'out_invoice',
            'partner_id': contract.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': contract.recurring_next_date,
            'origin': ', '.join(self.mapped('name')),
            'company_id': contract.company_id.id,
            'contract_id': contract.id,
            'user_id': contract.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.multi
    def _create_invoice(self):
        """Create the invoice from the source contracts.

        :param self: Contract records. Invoice header data will be obtained
          from the first record of this recordset.

        :return Created invoice record.
        """
        invoice_vals = self._prepare_invoice()
        invoice = self.env['account.invoice'].create(invoice_vals)
        for contract in self:
            old_date = fields.Date.from_string(
                contract.recurring_next_date or fields.Date.today(),
            )
            new_date = old_date + self.get_relalive_delta(
                contract.recurring_rule_type, contract.recurring_interval,
            )
            obj = self.with_context(
                old_date=old_date,
                next_date=new_date,
                # For correct evaluating of domain access rules + properties
                force_company=contract.company_id.id,
            )
            for line in contract.recurring_invoice_line_ids:
                invoice_line_vals = obj._prepare_invoice_line(line, invoice.id)
                self.env['account.invoice.line'].create(invoice_line_vals)
            contract.write({
                'recurring_next_date': new_date.strftime('%Y-%m-%d')
            })
        invoice.compute_taxes()
        return invoice

    @api.multi
    def _get_contracts2invoice(self, rest_contracts):
        """Method for being inherited by other modules to specify contract
        grouping rules. By default, each contract is invoiced separately.

        :param rest_contracts: Rest of the outstanding contracts to be invoiced
        """
        self.ensure_one()
        return self

    @api.multi
    def recurring_create_invoice(self):
        invoices = self.env['account.invoice']
        contracts = self
        while contracts:
            contracts2invoice = contracts[0]._get_contracts2invoice(contracts)
            contracts -= contracts2invoice
            invoices |= contracts2invoice._create_invoice()
        return invoices

    @api.model
    def cron_recurring_create_invoice(self):
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('account_type', '=', 'normal'),
             ('recurring_invoices', '=', True)])
        return contracts.recurring_create_invoice()

    @api.multi
    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref(
            'contract.email_contract_template',
            False,
        )
        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)
        ctx = dict(
            default_model='account.analytic.account',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
