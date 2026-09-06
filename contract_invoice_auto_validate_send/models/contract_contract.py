# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref=date_ref)
        to_send = moves.filtered(
            lambda move: move.state == "posted"
            and move.is_sale_document(include_receipts=True)
            and move.company_id.auto_send_contract_invoice
        )
        if to_send:
            # Queue the moves for the standard asynchronous "Send & Print" cron,
            # which sends each invoice with the customer's own method (email or
            # Peppol) without blocking the invoicing cron.
            to_send.sending_data = {
                "author_user_id": self.env.user.id,
                "author_partner_id": self.env.user.partner_id.id,
            }
            self.env.ref("account.ir_cron_account_move_send")._trigger()
        return moves
