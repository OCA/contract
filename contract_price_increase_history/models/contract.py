# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _apply_increase(self, increase):
        self.ensure_one()
        for line in self.contract_line_ids:
            line.with_context(price_unit_update_type="increase").write(
                {"price_unit": line.price_unit * (1 + increase.rate)}
            )
