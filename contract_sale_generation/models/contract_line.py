# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractLine(models.Model):
    _inherit = 'contract.line'

    @api.multi
    def _prepare_sale_line(self, order_id=False, sale_values=False):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        sale_line_vals = {
            'product_id': self.product_id.id,
            'quantity': self._get_quantity_to_invoice(*dates),
            'uom_id': self.uom_id.id,
            'discount': self.discount,
            'contract_line_id': self.id,
        }
        if order_id:
            sale_line_vals['order_id'] = order_id.id
        order_line = self.env['sale.order.line'].with_context(
            force_company=self.contract_id.company_id.id,
        ).new(sale_line_vals)
        if sale_values and not order_id:
            sale = self.env['sale.order'].with_context(
                force_company=self.contract_id.company_id.id,
            ).new(sale_values)
            order_line.order_id = sale
        # Get other order line values from product onchange
        order_line.product_id_change()
        sale_line_vals = order_line._convert_to_write(order_line._cache)
        # Insert markers
        name = self._insert_markers(dates[0], dates[1])
        sale_line_vals.update(
            {
                'sequence': self.sequence,
                'name': name,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'price_unit': self.price_unit,
            }
        )
        return sale_line_vals
