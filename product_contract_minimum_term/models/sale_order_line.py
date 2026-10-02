# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.contract_minimum_term.models.contract_minimum_term_mixin import (
    MINIMUM_TERM_FIELDS,
)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def create_contract_line(self, contract):
        """Upsell / downsell: the contract line is replaced by a new one that
        carries the commitment on, so the minimum term of the replaced line
        does not stand in the way of stopping or cancelling it.
        """
        return super(
            SaleOrderLine, self.with_context(min_term_skip_checks=True)
        ).create_contract_line(contract)

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        values = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id=predecessor_contract_line_id
        )
        if self._is_contract_minimum_term():
            values.update({fname: self[fname] for fname in MINIMUM_TERM_FIELDS})
            values["date_end"] = False
        else:
            # A fixed duration has no minimum term, even if the contract
            # template defines one
            values["min_term_interval"] = 0
        return values
