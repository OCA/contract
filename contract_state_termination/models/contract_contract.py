# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    state = fields.Selection(
        selection_add=[("terminated", "Terminated"), ("cancel",)],
        ondelete={"terminated": lambda records: records.write({"state": "active"})},
    )

    def _get_invoiceable_states(self):
        """A terminated contract may still raise its closing invoice.

        contract_termination stops the lines at the termination date; what
        was used up to that date can still be invoiced, so the state must not
        block it. Whether the recurring run picks terminated contracts up is
        contract_termination's call, not this module's.
        """
        return super()._get_invoiceable_states() + ["terminated"]

    def action_terminate_contract(self):
        """Only a running contract can be terminated.

        A draft contract never started, so there is nothing to end: it is
        cancelled instead. A terminated one may still update its details.
        """
        for contract in self:
            if contract.state not in ("active", "terminated"):
                raise UserError(
                    self.env._(
                        "Only an active contract can be terminated. "
                        "Cancel contract '%s' instead.",
                        contract.display_name,
                    )
                )
        return super().action_terminate_contract()

    def write(self, vals):
        """Follow `is_terminated`, whichever path sets or clears it.

        The termination wizard, *Cancel Termination* and any module that
        terminates a contract on its own all end in this field, so the state
        is kept in step here rather than on each of those methods.
        """
        if "is_terminated" not in vals or "state" in vals:
            return super().write(vals)
        if vals["is_terminated"]:
            return super().write(dict(vals, state="terminated"))
        reactivated = self.filtered(lambda contract: contract.state == "terminated")
        res = super().write(vals)
        reactivated.write({"state": "active"})
        return res

    @api.model
    def _sync_terminated_state(self):
        """Give the contracts terminated before installation their state."""
        self.with_context(active_test=False).search(
            [("is_terminated", "=", True), ("state", "!=", "terminated")]
        ).write({"state": "terminated"})
