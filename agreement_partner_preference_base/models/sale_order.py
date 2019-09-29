# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def onchange_partner_for_agreement(self):
        if self.partner_id.default_agreement_type_id:
            partner_agreement_type = self.partner_id.default_agreement_type_id
            if self.agreement_type_id != partner_agreement_type:
                self.agreement_type_id = partner_agreement_type
        self._update_agreement()

    def _prepare_sale_agreement_values(self):
        values = super()._prepare_sale_agreement_values()
        values.update(
            {
                'is_customer_requirement': False,
            }
        )
        return values
