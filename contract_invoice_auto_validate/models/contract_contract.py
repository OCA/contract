# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref=date_ref)
        for move in moves.filtered("invoice_line_ids"):
            if move.company_id.auto_post_contract_invoice:
                move.action_post()
        return moves
