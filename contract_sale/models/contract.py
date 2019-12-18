# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.multi
    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        overwrite Base Contract Method
        """
        invoices_values = []
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
            invoice_values = contract._prepare_invoice(date_ref)

            # Search Contract in sale order
            order_ids = self.env['sale.order'].search([
                ('partner_id', '=', contract.partner_id.id),
                ('contract_id', '=', contract.id),
            ])

            for line in contract_lines:
                invoice_values.setdefault('invoice_line_ids', [])
                invoice_line_values = line._prepare_invoice_line(
                    invoice_id=False
                )
                if invoice_line_values:

                    # Check Invoice and If It's Not Created then Updated Qty
                    for order_id in order_ids:
                        invoice_ids =\
                            order_id.order_line.mapped('invoice_lines')
                        if not invoice_ids:
                            for line in order_id.order_line:
                                if line.product_id.id == invoice_line_values.\
                                        get('product_id', False):
                                    invoice_line_values['quantity'
                                        ] += line.product_uom_qty

                    invoice_values['invoice_line_ids'].append(
                        (0, 0, invoice_line_values)
                    )

            invoices_values.append(invoice_values)
            contract_lines._update_recurring_next_date()
        return invoices_values

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
            'sale_order_line_id.order_id.contract_id'
        )
        res.get('domain')[0][2].extend(contracts)
        return res
