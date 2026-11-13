# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractTemplate(models.Model):
    _inherit = "contract.template"

    is_auto_renew = fields.Boolean(compute="_compute_is_auto_renew")

    @api.depends("contract_line_ids.is_auto_renew")
    def _compute_is_auto_renew(self):
        for record in self:
            record.is_auto_renew = all(
                line.is_auto_renew for line in record.contract_line_ids
            )
