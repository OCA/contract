# Copyright 2020 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("state")
    def _check_contact_is_not_terminated(self):
        for rec in self:
            if rec.state not in (
                "sale",
                "done",
                "cancel",
            ) and rec.order_line.filtered("contract_id.is_terminated"):
                raise ValidationError(
                    _("You can't upsell or downsell a terminated contract")
                )

