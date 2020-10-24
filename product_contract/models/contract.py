# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.translate import _


class ContractContract(models.Model):
    _inherit = "contract.contract"

    sale_order_count = fields.Integer(compute="_compute_sale_order_count")

    @api.depends("contract_line_ids")
    def _compute_sale_order_count(self):
        for rec in self:
            try:
                order_count = len(
                    rec.contract_line_ids.mapped("sale_order_line_id.order_id")
                )
            except AccessError:
                order_count = 0
            rec.sale_order_count = order_count

    def action_view_sales_orders(self):
        self.ensure_one()
        orders = self.contract_line_ids.mapped("sale_order_line_id.order_id")
        action = {
            "name": _("Sales Orders"),
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", orders.ids)],
        }
        if len(orders) == 1:
            # If there is only one order, open it directly
            action.update({"view_mode": "form", "res_id": orders.id})
        return action
