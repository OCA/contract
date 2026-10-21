# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, exceptions, models
from odoo.fields import first

_logger = logging.getLogger(__name__)


class Merge(models.TransientModel):
    _name = "contract.merge"
    _description = "Merge contracts"

    @api.model
    def _get_contracts(self):
        """Get contracts to merge."""
        contract_ids = self.env.context.get("active_ids")
        contracts = self.env["contract.contract"].browse(contract_ids).sorted()
        return contracts

    @api.model
    def _check(self, contracts):
        """Check that `contracts` are suitable for merge."""

        if len(contracts) <= 1:
            raise exceptions.UserError(
                self.env._("Please select at least 2 contracts to merge")
            )

        if len(contracts.partner_id) != 1:
            raise exceptions.UserError(
                self.env._("Selected contracts must have the same partner")
            )

    @api.model
    @api.private
    def new(self, *args, **kwargs):
        record = super().new(*args, **kwargs)
        contracts = self._get_contracts()
        self._check(contracts)
        return record

    @api.model
    def _update_foreign_keys(self, to_merge_contracts, result_contract):
        """
        Update foreign keys that link to
        `to_merge_contracts` to `result_contract`.
        """
        self.env["base.partner.merge.automatic.wizard"]._update_foreign_keys_generic(
            result_contract._name, to_merge_contracts, result_contract
        )

    @api.model
    def _update_reference_fields(self, to_merge_contracts, result_contract):
        """
        Update reference fields that link to
        `to_merge_contracts` to `result_contract`.
        """
        self.env[
            "base.partner.merge.automatic.wizard"
        ]._update_reference_fields_generic(
            result_contract._name, to_merge_contracts, result_contract
        )

    def _merge(self, contracts):
        """Merge `contracts` in one contract and return it."""
        result_contract = first(contracts)
        to_merge_contracts = contracts - result_contract

        self._update_foreign_keys(to_merge_contracts, result_contract)
        self._update_reference_fields(to_merge_contracts, result_contract)

        _logger.info(
            "User #%s merged the contracts %r into %s",
            self.env.uid,
            to_merge_contracts.ids,
            result_contract.id,
        )

        to_merge_contracts.unlink()

        return result_contract

    def run(self):
        contracts = self._get_contracts()
        return self._merge(contracts).get_formview_action()
