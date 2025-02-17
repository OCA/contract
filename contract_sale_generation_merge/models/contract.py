# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    merge_sales_orders = fields.Boolean(
        string="Merge Existing Orders",
        help="If enabled, contract lines will be added to an existing sales order "
        "with the same commitment (delivery) date instead of creating a new one.",
    )

    def _recurring_create_sale(self, date_ref=False):
        sales_values_list = self._prepare_recurring_sales_values(date_ref)
        sale_orders = self.env["sale.order"]
        new_sale_values = []

        for contract, sale_values in zip(self, sales_values_list):
            existing_sale = (
                contract._get_existing_sale(sale_values)
                if contract.merge_sales_orders
                else None
            )

            if existing_sale:
                contract._add_contract_lines(existing_sale)
                sale_orders |= existing_sale
            else:
                new_sale_values.append(sale_values)

        if new_sale_values:
            sale_orders |= self.env["sale.order"].create(new_sale_values)

        sale_orders.filtered(lambda sale: sale.contract_auto_confirm).action_confirm()
        self._compute_recurring_next_date()
        return sale_orders

    def _get_existing_sale(self, sale_values):
        """Find an existing active sale order for the same partner
        within the same day (commitment date)."""
        date_only = sale_values["date_order"].date()
        date_start = datetime.combine(date_only, datetime.min.time())
        date_end = datetime.combine(date_only + timedelta(days=1), datetime.min.time())

        return self.env["sale.order"].search(
            [
                ("partner_id", "=", sale_values["partner_id"]),
                ("commitment_date", ">=", date_start),
                ("commitment_date", "<", date_end),
                ("state", "not in", ["cancel", "done"]),
            ],
            limit=1,
        )

    def _add_contract_lines(self, existing_sale):
        """Add contract lines to an existing sale order."""
        for contract_line in self.contract_line_ids:
            sale_line_vals = contract_line._prepare_sale_line(order_id=existing_sale)
            existing_sale.write({"order_line": [(0, 0, sale_line_vals)]})
