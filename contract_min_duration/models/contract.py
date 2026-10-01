# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    min_contract_end_date = fields.Date(
        string="Minimum End Date",
        help="The contract cannot end before this date. "
        "If a termination or end date is set earlier, "
        "it will be automatically extended to this date.",
    )

    def write(self, vals):
        if "date_end" not in vals and "min_contract_end_date" not in vals:
            return super().write(vals)

        for contract in self:
            _vals = vals.copy()
            min_date_str = (
                _vals["min_contract_end_date"]
                if "min_contract_end_date" in _vals
                else contract.min_contract_end_date
            )
            end_date_str = (
                _vals["date_end"] if "date_end" in _vals else contract.date_end
            )

            if min_date_str and end_date_str:
                min_date = fields.Date.to_date(min_date_str)
                end_date = fields.Date.to_date(end_date_str)
                if end_date < min_date:
                    _vals["date_end"] = min_date_str
            super(ContractContract, contract).write(_vals)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            min_date_str = vals.get("min_contract_end_date")
            end_date_str = vals.get("date_end")
            if min_date_str and end_date_str:
                min_date = fields.Date.to_date(min_date_str)
                end_date = fields.Date.to_date(end_date_str)
                if min_date and end_date and end_date < min_date:
                    vals["date_end"] = min_date_str
        return super().create(vals_list)
