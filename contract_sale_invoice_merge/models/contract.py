# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = ["contract.contract", "account.move.group.mixin"]

    @api.model
    def _get_invoice_grouping_dict(self):
        self.ensure_one()
        return {
            "partner_invoice_id": self.invoice_partner_id.id,
            "payment_term_id": self.payment_term_id.id,
            "user_id": self.user_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "journal_id": self.journal_id.id,
        }

    def _get_group_invoice_domain(self, date_ref):
        return self._get_contracts_to_invoice_domain(date_ref)

    def _prepare_group_invoices_values(self, date_ref):
        return self._prepare_recurring_invoices_values(date_ref)

    def _hook_post_create_group_invoices(self, moves):
        self._add_contract_origin(moves)
        self._invoice_followers(moves)
        self._compute_recurring_next_date()
