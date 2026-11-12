# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agreement_template_id = fields.Many2one(
        "agreement", string="Agreement Template", domain="[('is_template', '=', True)]"
    )

    def _action_confirm(self):
        res = super()._action_confirm()
        for order in self:
            if order.agreement_template_id:
                order.agreement_id = order.agreement_template_id.copy(
                    default={
                        "name": order.name,
                        "code": order.name,
                        "is_template": False,
                        "sale_id": order.id,
                        "partner_id": order.partner_id.id,
                    }
                )
                for line in order.order_line.filtered(
                    lambda line: not line.display_type
                ):
                    # Create agreement line
                    self.env["agreement.line"].create(
                        self._get_agreement_line_vals(line)
                    )
                    # Create SP's based on product_id config
                    if line.product_id.service_tracking == "serviceprofile":
                        self.create_sp_qty(line, order)
        return res

    def create_sp_qty(self, line, order):
        """Create line.product_uom_qty SP's"""
        if line.product_id.product_tmpl_id.service_tracking == "serviceprofile":
            for i in range(1, int(line.product_uom_qty) + 1):
                self.env["agreement.serviceprofile"].create(
                    self._get_sp_vals(line, order, i)
                )

    def _get_agreement_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "name": line.name,
            "agreement_id": line.order_id.agreement_id.id,
            "qty": line.product_uom_qty,
            "sale_line_id": line.id,
            "uom_id": line.product_uom.id,
        }

    def _get_sp_vals(self, line, order, i):
        return {
            "name": line.name + " " + str(i),
            "product_id": line.product_id.product_tmpl_id.id,
            "agreement_id": order.agreement_id.id,
        }
