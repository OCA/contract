# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_sale_line_vals(self, dates, order_id=False):
        sale_line_vals = {
            "product_id": self.product_id.id,
            "product_uom_qty": self._get_quantity_to_invoice(*dates),
            "product_uom": self.uom_id.id,
            "discount": self.discount,
            "contract_line_id": self.id,
            "display_type": self.display_type,
        }
        if order_id:
            sale_line_vals["order_id"] = order_id.id
        return sale_line_vals

    def _prepare_sale_line(self, order_id=False, sale_values=False):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        sale_line_vals = self._prepare_sale_line_vals(dates, order_id)

        order_line = (
            self.env["sale.order.line"]
            .with_company(self.contract_id.company_id.id)
            .new(sale_line_vals)
        )
        if sale_values and not order_id:
            sale = (
                self.env["sale.order"]
                .with_company(self.contract_id.company_id.id)
                .new(sale_values)
            )
            order_line.order_id = sale
        # Get other order line values from product onchange
        order_line.product_id_change()
        sale_line_vals = order_line._convert_to_write(order_line._cache)
        # Insert markers
        name = self._insert_markers(dates[0], dates[1])
        sale_line_vals.update(
            {
                "sequence": self.sequence,
                "name": name,
                "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
                "price_unit": self.price_unit,
            }
        )
        return sale_line_vals
