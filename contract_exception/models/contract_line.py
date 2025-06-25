# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = ["contract.line", "base.exception.method"]
    _name = "contract.line"

    ignore_exception = fields.Boolean(
        related="contract_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("contract_id")

    @api.model
    def _reverse_field(self):
        return "contract_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("contract_id")
