# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_display_line_contracts(self, order_lines, position):
        """Return the contracts a section/note line must be propagated to.

        - A section spans the product lines up to the next section and is
          propagated to every contract having products in that span, so a
          section shared by several contracts is repeated in each of them.
        - A note belongs to the product line above it and is propagated to
          that line's contract.
        """
        self.ensure_one()
        if self.display_type == "line_section":
            return self._get_section_span_contracts(order_lines[position + 1 :])
        return self._get_note_contract(reversed(order_lines[:position]))

    def _get_section_span_contracts(self, following_lines):
        self.ensure_one()
        contracts = self.env["contract.contract"]
        for line in following_lines:
            if line.display_type == "line_section":
                break
            if line.display_type == "line_note":
                continue
            if line.contract_id:
                contracts |= line.contract_id
        return contracts

    def _get_note_contract(self, candidate_lines):
        """Return the contract of the nearest adjacent product line, if any."""
        self.ensure_one()
        for line in candidate_lines:
            if line.display_type:
                break
            return line.contract_id
        return self.env["contract.contract"]

    def _contract_already_has_display_line(self, contract):
        """Return whether the contract already carries this section/note.

        Prevents duplicates when the same order is processed twice and when an
        upsell/downsell order repeats a display line the contract already has.
        The line is matched by its originating order line or, for lines coming
        from another order, by display type and text.
        """
        self.ensure_one()
        return bool(
            contract.contract_line_ids.filtered(
                lambda cl: cl.display_type == self.display_type
                and (cl.sale_order_line_id == self or cl.name == self.name)
            )
        )

    def _prepare_contract_line_section_values(self, contract):
        self.ensure_one()
        return {
            "sequence": self.sequence,
            "display_type": self.display_type,
            "name": self.name,
            "contract_id": contract.id,
            "sale_order_line_id": self.id,
            # A start date is required to satisfy the recurring-date constraint
            # on line-recurrence contracts, even though sections never invoice.
            "date_start": contract.date_start
            or self.date_start
            or fields.Date.context_today(self),
        }
