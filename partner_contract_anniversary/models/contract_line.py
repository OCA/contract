# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):
    _inherit = "contract.line"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Update contract anniversary
        self.env["res.partner"]._update_contract_anniversary(records.partner_id.ids)
        return records

    def write(self, values):
        res = super().write(values)
        # Update contract anniversary
        if "start_date" in values:
            self.env["res.partner"]._update_contract_anniversary(self.partner_id.ids)
        return res
