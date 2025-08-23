# Copyright 2020 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "sale.order.line.contract.mixin"]

    @api.constrains("contract_id")
    def _check_contact_is_not_terminated(self):
        for rec in self:
            if (
                rec.order_id.state not in ("sale", "done", "cancel")
                and rec.contract_id.is_terminated
            ):
                raise ValidationError(
                    _("You can't upsell or downsell a terminated contract")
                )

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        res = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id
        )
        res["termination_notice_interval"] = self.product_id.termination_notice_interval
        res["termination_notice_rule_type"] = self.product_id.termination_notice_rule_type
        res["manual_renew_needed"] = self.manual_renew_needed
        res["automatic_price"] = self.automatic_price
        return res
