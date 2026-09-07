# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref=date_ref)
        to_send = moves.filtered(
            lambda move: move.state == "posted"
            and move.is_sale_document(include_receipts=True)
            and move.company_id.auto_send_contract_invoice
        )
        if not to_send:
            return moves
        send_cron = self.env.ref(
            "account.ir_cron_account_move_send", raise_if_not_found=False
        )
        if not (send_cron and send_cron.sudo().active):
            # Without an active cron the invoices would keep sending_data set
            # forever without ever being sent, so leave them untouched.
            _logger.warning(
                "Contract invoices %s are configured for automatic sending, but "
                "the 'Send invoices automatically' cron is not active. They will "
                "not be sent automatically.",
                to_send.ids,
            )
            return moves
        for move in to_send:
            company = move.company_id
            # Queue the move for the standard asynchronous "Send & Print" cron,
            # which sends the invoice with the customer's own method (email or
            # Peppol) without blocking the invoicing cron.
            move.sending_data = {
                "author_user_id": self.env.user.id,
                "author_partner_id": (
                    company.auto_send_author_partner_id or company.partner_id
                ).id,
            }
        send_cron._trigger()
        return moves
