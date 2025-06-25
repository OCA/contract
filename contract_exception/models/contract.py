# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Contract(models.Model):
    _inherit = ["contract.contract", "base.exception"]
    _name = "contract.contract"

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._contract_check_exception(vals)
        return record

    def write(self, vals):
        result = super().write(vals)
        self._contract_check_exception(vals)
        return result

    @api.model
    def _reverse_field(self):
        return "contract_ids"

    def _fields_trigger_check_exception(self):
        return ["ignore_exception", "contract_line_ids"]

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        lines = self.mapped("contract_line_ids")
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    def _contract_check_exception(self, vals):
        check_exceptions = any(
            field in vals for field in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            self.detect_exceptions()

    @api.model
    def test_all_contracts(self):
        contract_set = self.search([])
        contract_set.detect_exceptions()
        return True

    @api.model
    def _get_popup_action(self):
        return self.env.ref("contract_exception.action_contract_exception_confirm")
