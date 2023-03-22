# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"
    _rec_name = "display_name"

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        required=False,
        copy=False,
    )

    def _prepare_invoice_line(self, move_form):
        res = super(ContractLine, self)._prepare_invoice_line(move_form)
        if self.sale_order_line_id and res:
            res["sale_line_ids"] = [(6, 0, [self.sale_order_line_id.id])]
        return res

    def _get_auto_renew_rule_type(self):
        """monthly last day don't make sense for auto_renew_rule_type"""
        self.ensure_one()
        if self.recurring_rule_type == "monthlylastday":
            return "monthly"
        return self.recurring_rule_type

    @api.onchange("product_id")
    def _onchange_product_id_recurring_info(self):
        for rec in self:
            rec.date_start = fields.Date.today()
            if rec.product_id.is_contract:
                rec.update(
                    {
                        "recurring_rule_type": rec.product_id.recurring_rule_type,
                        "recurring_invoicing_type": rec.product_id.recurring_invoicing_type,
                        "recurring_interval": 1,
                        "is_auto_renew": rec.product_id.is_auto_renew,
                        "auto_renew_interval": rec.product_id.auto_renew_interval,
                        "auto_renew_rule_type": rec.product_id.auto_renew_rule_type,
                        "termination_notice_interval": (
                            rec.product_id.termination_notice_interval
                        ),
                        "termination_notice_rule_type": (
                            rec.product_id.termination_notice_rule_type
                        ),
                    }
                )
