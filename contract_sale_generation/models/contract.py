# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class ContractContract(models.Model):
    _inherit = 'contract.contract'

    type = fields.Selection(
        string='Type',
        selection=[('invoice', 'Invoice'),
                   ('sale', 'Sale')],
        default='invoice',
        required=True,
    )
    sale_autoconfirm = fields.Boolean(string='Sale autoconfirm')
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    sale_count = fields.Integer(compute="_compute_sale_count")
    invoice_group_method_id = fields.Many2one(comodel_name="sale.invoice.group.method")

    @api.multi
    def action_show_sales(self):
        self.ensure_one()
        tree_view_ref = (
            'sale.view_quotation_tree_with_onboarding'
        )
        form_view_ref = (
            'sale.view_order_form'
        )
        tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        form_view = self.env.ref(form_view_ref, raise_if_not_found=False)
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Commandes'),
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'domain': [('id', 'in', self._get_related_sale_orders().ids)],
        }
        if tree_view and form_view:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action

    @api.multi
    def _get_related_sale_orders(self):
        """ Only sale order generated from this contract """
        self.ensure_one()
        return self.env['sale.order'].search(
                [('contract_id', '=', self.id)])


    @api.multi
    def _compute_sale_count(self):
        for rec in self:
            rec.sale_count = len(rec._get_related_sale_orders())


    @api.multi
    def _prepare_recurring_sales_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        sales = self.env['sale.order']
        sol_model = self.env['sale.order.line']
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            sale_values = contract._prepare_sale(date_ref)
            so_id = self.env['sale.order'].create(sale_values)
            for line in contract_lines:
                sale_line_values = line._prepare_sale_line(order_id=so_id)
                sol_model.create(sale_line_values)
            sales |= so_id
            contract_lines._update_recurring_next_date()
        return sales


    @api.multi
    def _prepare_sale(self, date_ref):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(
                _("You must first select a Customer for Contract %s!") %
                self.name)
        sale = self.env['sale.order'].new({
            'partner_id': self.partner_id,
            'date_order': '%s 00:00:00' % date_ref,
            'expected_date': '%s 00:00:00' % date_ref,
            'origin': self.name,
            'client_order_ref': self.client_order_ref or '',
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'contract_id': self.id,
            'require_signature': False,
            'require_payment': False,
        })
        # Get other sale values from partner onchange
        sale.onchange_partner_id()
        sale.partner_invoice_id = self.invoice_partner_id
        sale.payment_term_id = self.payment_term_id
        sale.payment_mode_id = self.payment_mode_id
        sale.fiscal_position_id = self.fiscal_position_id
        sale.pricelist_id = self.pricelist_id
        sale.invoice_group_method_id = self.invoice_group_method_id
        sale.mandate_id = self.mandate_id
        sale.analytic_account_id = self.group_id
#         sale.agreement_id = self.agreement_id
        
        return sale._convert_to_write(sale._cache)


    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        contracts = self.filtered(lambda c: c.type != 'sale')
        if contracts :
            return super(ContractContract, contracts)._recurring_create_invoice(date_ref=date_ref)
        else:
            return self.env['account.invoice']
        

    @api.multi
    def _finalize_and_create_sales(self, sales_values):
        """
        Create Sale orders
        @param sales_values: dictionnary fo values
        @return: MUST return a sale.order recordset
        """
        sale_model = self.env['sale.order']
        sales = self.env['sale.order']
        for so_id in sales_values:
#             so_id = sale_model.create(so_vals)
            if self.sale_autoconfirm:
                so_id.action_confirm()
            sales |= so_id
        return sales


    @api.multi
    def _recurring_create_sales(self, date_ref=False):
        for contract in self:
            sales_values = contract._prepare_recurring_sales_values(date_ref)
            contract._finalize_and_create_sales(sales_values)

    @api.multi
    def recurring_create_sale(self, ):
        self._recurring_create_sales()
        return True


    @api.model
    def cron_recurring_create_sale(self, date_ref=None):
        domain = self._get_contracts_to_invoice_domain()
        domain.append(('type', '=', 'sale'))
        contracts_to_invoice = self.search(domain)
        _logger.debug("Found countracts %s for recurring creation" % contracts_to_invoice)
        date_ref = fields.Date.context_today(contracts_to_invoice)
        contracts_to_invoice._recurring_create_sales(date_ref)
