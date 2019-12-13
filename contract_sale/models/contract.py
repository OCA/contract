# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.multi
    def _prepare_recurring_invoices_values(self, date_ref=False):
        invoices_values =   super(ContractContract, self).\
            _prepare_recurring_invoices_values(date_ref=date_ref)
        return invoices_values

    def _compute_sale_order_count(self):
        super(ContractContract, self)._compute_sale_order_count()
        contract_count = self.contract_line_ids.\
            mapped('sale_order_line_id.order_id.contract_id')
        self.sale_order_count += contract_count

    @api.multi
    def action_view_sales_orders(self):
        res = super(ContractContract, self).action_view_sales_orders()
        contracts = self.contract_line_ids.mapped(
            'sale_order_line_id.order_id.contract_id'
        )
        res.get('domain')[0][2].extend(contracts)
        return res
