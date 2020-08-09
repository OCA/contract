# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ContractLine(models.Model):
    _inherit = 'contract.line'
    
        
    @api.multi
    def _prepare_sale_line(self, order_id=False):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        line_vals = {
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.uom_id.id,
#             'contract_line_id': self.id,
            'created_from_contract_line_id': self.id,
        }
        if order_id:
            line_vals.update({'order_id': order_id.id})
        sale_line = self.env['sale.order.line'].new(line_vals)
        # Get other sale line values from product onchange
        sale_line.product_id_change()
        sale_line_vals = sale_line._convert_to_write(sale_line._cache)
        
        # Insert markers
        name = self._insert_markers(dates[0], dates[1])
        sale_line_vals.update({
            'name': name,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'product_uom_qty': self._get_quantity_to_invoice(*dates),
            'product_uom': self.uom_id.id,
        })
        return sale_line_vals
        
#         
#     @api.multi
#     def _prepare_invoice_line(self, invoice_id=False):
#         self.ensure_one()
#         dates = self._get_period_to_invoice(
#             self.last_date_invoiced, self.recurring_next_date
#         )
#         invoice_line_vals = {
#             'product_id': self.product_id.id,
#             'quantity': self._get_quantity_to_invoice(*dates),
#             'uom_id': self.uom_id.id,
#             'discount': self.discount,
#             'contract_line_id': self.id,
#         }
#         if invoice_id:
#             invoice_line_vals['invoice_id'] = invoice_id.id
#         invoice_line = self.env['account.invoice.line'].new(invoice_line_vals)
#         # Get other invoice line values from product onchange
#         invoice_line._onchange_product_id()
#         invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
#         # Insert markers
#         name = self._insert_markers(dates[0], dates[1])
#         invoice_line_vals.update(
#             {
#                 'name': name,
#                 'account_analytic_id': self.analytic_account_id.id,
#                 'price_unit': self.price_unit,
#             }
#         )
#         return invoice_line_vals
