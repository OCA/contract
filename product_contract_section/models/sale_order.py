# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_create_contract(self):
        contracts = super().action_create_contract()
        for order in self:
            if order.is_contract:
                order._create_contract_section_lines()
        return contracts

    def _create_contract_section_lines(self):
        """Create contract lines for the order's section and note lines.

        Base ``product_contract`` only creates contract lines for order lines
        whose product is a contract, so sections and notes are dropped. Here we
        recreate them on the relevant contract(s), keeping the order's sequence
        so the layout is preserved. Sections follow the products they span and
        notes follow the line they are attached to (previous or next).

        Upsell/downsell orders add lines to an existing contract that may
        already carry the display line, so it is only created when the contract
        does not already have an equivalent one.
        """
        self.ensure_one()
        contract_line_model = self.env["contract.line"]
        order_lines = self.order_line.sorted(lambda line: (line.sequence, line.id))
        for position, line in enumerate(order_lines):
            if not line.display_type:
                continue
            contracts = line._get_display_line_contracts(order_lines, position)
            for contract in contracts:
                if line._contract_already_has_display_line(contract):
                    continue
                contract_line_model.create(
                    line._prepare_contract_line_section_values(contract)
                )
