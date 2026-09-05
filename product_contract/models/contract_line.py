# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command, api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"
    _rec_name = "display_name"

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        required=False,
        copy=False,
    )

    def _prepare_invoice_line(self):
        res = super()._prepare_invoice_line()
        if self.sale_order_line_id and res:
            res["sale_line_ids"] = [Command.set([self.sale_order_line_id.id])]
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

    def _set_recurrence_field(self, field):
        res = super()._set_recurrence_field(field)
        for record in self:
            if record.product_id.is_contract and field in record.product_id:
                record[field] = record.product_id[field]
        return res

    @api.depends(
        "contract_id.recurring_rule_type", "contract_id.line_recurrence", "product_id"
    )
    def _compute_recurring_rule_type(self):
        return super()._compute_recurring_rule_type()

    @api.depends(
        "contract_id.recurring_invoicing_type",
        "contract_id.line_recurrence",
        "product_id",
    )
    def _compute_recurring_invoicing_type(self):
        return super()._compute_recurring_invoicing_type()

    @api.depends(
        "contract_id.recurring_interval", "contract_id.line_recurrence", "product_id"
    )
    def _compute_recurring_interval(self):
        return super()._compute_recurring_interval()
