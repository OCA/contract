# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        invoices = super()._recurring_create_invoice(date_ref)
        for contract_to_invoice in self:
            product_avg_qty_dict = {}
            for each_contract_line in contract_to_invoice.contract_line_ids.\
                    filtered(lambda l: l.products_invoiced_by_avg_ids):
                for each_avg_product in each_contract_line.products_invoiced_by_avg_ids:
                    product_avg_qty_dict.update(
                        {each_avg_product.id: each_contract_line.quantity})
        for each_invoice in invoices:
            for each_inv_line in each_invoice.invoice_line_ids:
                if each_inv_line.product_id.id in list(product_avg_qty_dict.keys()):
                    qty = product_avg_qty_dict.get(
                        each_inv_line.product_id.id) / each_inv_line.quantity
                    each_inv_line.quantity = round(qty)
                    each_inv_line._onchange_product_id_account_invoice_pricelist()
        return invoices


class ContractLine(models.Model):
    _inherit = 'contract.line'

    products_invoiced_by_avg_ids = fields.Many2many(
        comodel_name='product.product',
        relation='contract_line_product_id_rel',
        column1='contract_line_id',
        column2='product_id',
        string='Products Invoiced using Average Quantity')
