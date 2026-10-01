# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.account.models.account_move import AccountMove


class AccountMoveGroupMixin(models.AbstractModel):
    _name = "account.move.group.mixin"
    _description = (
        "Interface for models that participate in account move grouped invoicing"
    )

    do_not_group_move = fields.Boolean(
        string="Don't group this model in one invoice",
        default=lambda self: self.env["res.config.settings"].do_not_group_move,
    )

    def _get_invoice_grouping_dict(self):
        """Return grouping values."""
        return {}

    @api.model
    def _get_group_invoice_domain(self, date_ref):
        """Return the domain for records to invoice."""
        return []

    def _prepare_group_invoices_values(self, date_ref):
        """Return recurring invoice values."""
        raise NotImplementedError

    def _hook_post_create_group_invoices(self, moves: AccountMove):
        """Hook right after the creation of grouped invoices."""
        return
