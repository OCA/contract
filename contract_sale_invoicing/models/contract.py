# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    invoicing_sales = fields.Boolean(
        string='Invoice Pending Sales Orders',
        help='Include sales to invoice on the contract invoice.')
    filter_with = fields.Selection([
        ('analytic_account', 'Analytic Account'),
        ('contract', 'Contract')],
        default='analytic_account', string='Filter with the same',
        help="Select the sale orders with the same analytic account or "
             "contract")
    group_by = fields.Selection([
        ('sale_order', 'Sale Order'),
        ('contract', 'Contract')],
        default='sale_order', string='Create one invoice per')

    def get_sale_order_domain(self):
        domain = [
            ('partner_invoice_id', 'child_of',
             self.partner_id.commercial_partner_id.ids),
            ('invoice_status', '=', 'to invoice'),
            ('date_order', '<=',
             '{} 23:59:59'.format(self.recurring_next_date)),
            ]
        if self.filter_with == 'analytic_account':
            domain.append(('analytic_account_id', '=', self.group_id.id))
        elif self.filter_with == 'contract':
            domain.append(('contract_id', '=', self.id))
        return domain

    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        invoices = super()._recurring_create_invoice(date_ref)
        for rec in self:
            if not rec.invoicing_sales:
                return invoices
            so_domain = rec.get_sale_order_domain()
            sales = self.env['sale.order'].search(so_domain)
            if sales and self.group_by == 'sale_order':
                invoice_ids = sales.action_invoice_create()
                invoices |= self.env['account.invoice'].browse(invoice_ids)[:1]

    @api.multi
    def _prepare_invoice_line_dict(self, contract_line_rec, invoice_line,
                                   remain_qty):
        return {
            'invoice_id': False,
            'uom_id': contract_line_rec.uom_id.id,
            'product_id': invoice_line.get('product_id'),
            'quantity': remain_qty or 0,
            'discount': contract_line_rec.discount,
            'contract_line_id': contract_line_rec.id,
            'name': contract_line_rec.name,
            'account_analytic_id': False,
            'price_unit': contract_line_rec.price_unit
        }

    @api.multi
    def _prepare_recurring_invoices_values(self, date_ref=False):
        invoices_values = super()._prepare_recurring_invoices_values()
        updated_invoices_values = []
        for invoice_val in invoices_values:
            invoice_line_values = {}
            invoice_line_list = []
            for invoice_line in invoice_val.get('invoice_line_ids', []):
                invoice_line = invoice_line[2] or {}
                contract_line_rec = self.env['contract.line'].\
                    browse(invoice_line.get('contract_line_id', False))
                if contract_line_rec and contract_line_rec.contract_id and\
                        contract_line_rec.contract_id.invoicing_sales and \
                        contract_line_rec.contract_id.group_by == 'contract':
                    so_domain = \
                        contract_line_rec.contract_id.get_sale_order_domain()
                    order_ids = self.env['sale.order'].search(so_domain)
                    sale_order_line_product_qty = {}
                    for order_id in order_ids:
                        if not order_id.order_line.mapped('invoice_lines'):
                            for line in order_id.order_line:
                                if sale_order_line_product_qty.\
                                        get(line.product_id.id):
                                    sale_order_line_product_qty[
                                        line.product_id.id
                                        ] += line.product_uom_qty
                                else:
                                    sale_order_line_product_qty[
                                        line.product_id.id
                                        ] = line.product_uom_qty
                    if invoice_line.get('product_id'
                                        ) in sale_order_line_product_qty:
                        if sale_order_line_product_qty.\
                                get(line.product_id.id
                                    ) > invoice_line.get('quantity'):
                            remain_qty = sale_order_line_product_qty.\
                                get(invoice_line.get('product_id')
                                    ) - invoice_line.get('quantity') or 0
                            invoice_line_values =\
                                self._prepare_invoice_line_dict(
                                    contract_line_rec, invoice_line, remain_qty
                                    ) or {}
                            invoice_line_list.append(invoice_line_values)
                            sale_order_line_product_qty.\
                                pop(invoice_line.get('product_id'))
            invoice_val['invoice_line_ids'] +=\
                [(0, 0, invoice_line_val
                  )for invoice_line_val in invoice_line_list]
            updated_invoices_values.append(invoice_val)
        return updated_invoices_values

    @api.depends('contract_line_ids')
    def _compute_sale_order_count(self):
        super(ContractContract, self)._compute_sale_order_count()
        contract_count = len(
            self.contract_line_ids.
            mapped('sale_order_line_id.order_id.contract_id')) or 0
        self.sale_order_count += contract_count

    @api.multi
    def action_view_sales_orders(self):
        res = super(ContractContract, self).action_view_sales_orders()
        contracts = self.contract_line_ids.mapped(
            'sale_order_line_id.order_id.contract_id')
        res.get('domain')[0][2].extend(contracts)
        return res
