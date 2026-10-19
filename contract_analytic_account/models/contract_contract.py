# Copyright 2026 Cristiano Mafra Junior - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = ["contract.contract", "analytic.mixin"]

    def _sync_lines_analytic_distribution(self):
        for contract in self:
            if not contract.analytic_distribution:
                continue
            contract.contract_line_ids.analytic_distribution = (
                contract.analytic_distribution
            )

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        self._sync_lines_analytic_distribution()

    @api.model_create_multi
    def create(self, vals_list):
        contracts = super().create(vals_list)
        contracts._sync_lines_analytic_distribution()
        return contracts

    def write(self, vals):
        res = super().write(vals)
        if "analytic_distribution" in vals:
            self._sync_lines_analytic_distribution()
        return res
