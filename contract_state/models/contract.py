# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("cancel", "Cancelled"),
        ],
        default="active",
        required=True,
        copy=False,
        tracking=True,
        help="A contract only generates invoices while it is active. Draft is "
        "for a contract still being prepared, cancelled for one that will "
        "never run.",
    )

    def _get_invoiceable_states(self):
        """Return the states in which a contract may generate invoices.

        Extension point. A module that adds a state which should also invoice
        overrides this rather than touching the visibility compute or the
        invoicing domain, both of which read it.
        """
        return ["active"]

    @api.depends("state")
    def _compute_create_invoice_visibility(self):
        """Hide the invoicing button outside the invoiceable states.

        `create_invoice_visibility` already drives the button on the form, so
        extending it keeps the gate in one place instead of spreading
        `state` checks through the views.
        """
        res = super()._compute_create_invoice_visibility()
        invoiceable_states = self._get_invoiceable_states()
        for contract in self:
            if contract.state not in invoiceable_states:
                contract.create_invoice_visibility = False
        return res

    def _get_contracts_to_invoice_domain(self, date_ref=None):
        """Keep contracts that are not invoiceable out of the cron."""
        domain = super()._get_contracts_to_invoice_domain(date_ref=date_ref)
        return domain & fields.Domain([("state", "in", self._get_invoiceable_states())])

    def recurring_create_invoice(self):
        """Refuse to invoice a contract that is not in an invoiceable state.

        Hiding the button is not enough on its own. The action is reachable
        from the wizard, from a server action, from the shell and from any
        module that calls it, and a rule about when a contract may be billed
        should not depend on whether a particular view managed to hide a
        button.
        """
        blocked = self.filtered(
            lambda contract: contract.state not in contract._get_invoiceable_states()
        )
        if blocked:
            raise ValidationError(
                self.env._(
                    "These contracts cannot be invoiced in their current "
                    "state:\n- %(names)s",
                    names="\n- ".join(blocked.mapped("display_name")),
                )
            )
        return super().recurring_create_invoice()

    def action_activate(self):
        return self.write({"state": "active"})

    def action_cancel(self):
        return self.write({"state": "cancel"})

    def action_draft(self):
        return self.write({"state": "draft"})
