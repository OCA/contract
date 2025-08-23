# Copyright 2025 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    @api.onchange("product_id")
    def _onchange_product_id_termination_info(self):
        for rec in self:
            rec.date_start = fields.Date.today()
            if rec.product_id.is_contract:
                rec.update(
                    {
                        "termination_notice_interval": (
                            rec.product_id.termination_notice_interval
                        ),
                        "termination_notice_rule_type": (
                            rec.product_id.termination_notice_rule_type
                        ),
                        "manual_renew_needed": (
                            rec.product_id.manual_renew_needed
                        ),
                        "automatic_price": (
                            rec.product_id.automatic_price
                        ),
                    }
                )
