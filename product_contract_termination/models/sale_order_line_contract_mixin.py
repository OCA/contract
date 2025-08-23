# Copyright 2020 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLineContractMixin(models.AbstractModel):
    _inherit = "sale.order.line.contract.mixin"

    automatic_price = fields.Boolean(
        string="Auto Price",
        compute="_compute_product_contract_termination_data",
        precompute=True,
        default=False,
        store=True,
        readonly=False,
    )

    manual_renew_needed = fields.Boolean(
        string="Manual Renenew Needed",
        help="This flag is used to make a difference between a definitive stop"
         "and temporary one for which a user is not able to plan a"
         "successor in advance",
    )

    termination_notice_interval = fields.Integer(
        default=1,
        string="Termination Notice Before",
    )

    termination_notice_rule_type = fields.Selection(
        [("daily", "Day(s)"), ("weekly", "Week(s)"), ("monthly", "Month(s)")],
        default="monthly",
        string="Termination Notice type",
    )

    @api.depends("product_id")
    def _compute_product_contract_termination_data(self):
        for rec in self:
            vals = {
                "termination_notice_interval": False,
                "termination_notice_rule_type": False,
                "automatic_price": False,
                "manual_renew_needed": False,
            }
            if rec.product_id.is_contract:
                p = rec.product_id
                vals = {
                    "termination_notice_interval": p.termination_notice_interval,
                    "termination_notice_rule_type": p.termination_notice_rule_type,
                    "automatic_price": p.automatic_price,
                    "manual_renew_needed": p.manual_renew_needed,
                }
            rec.update(vals)
