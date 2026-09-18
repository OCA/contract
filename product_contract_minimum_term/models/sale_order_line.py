# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.contract_minimum_term.models.contract_minimum_term_mixin import (
    MINIMUM_TERM_FIELDS,
)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains("contract_duration_type", "is_auto_renew")
    def _check_contract_duration_type(self):
        for line in self:
            if line._is_contract_minimum_term() and line.is_auto_renew:
                raise ValidationError(
                    self.env._(
                        "The line %(line)s has a minimum term: it cannot be "
                        "renewed automatically.",
                        line=line.name,
                    )
                )

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        values = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id=predecessor_contract_line_id
        )
        if self._is_contract_minimum_term():
            values.update({fname: self[fname] for fname in MINIMUM_TERM_FIELDS})
            values.update({"date_end": False, "is_auto_renew": False})
        else:
            # A fixed duration has no minimum term, even if the contract
            # template defines one
            values.update(
                {
                    "min_term_interval": 0,
                    "min_term_renewal_interval": 0,
                    "min_term_notice_interval": 0,
                }
            )
        return values
