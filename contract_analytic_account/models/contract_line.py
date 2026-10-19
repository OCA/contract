# Copyright 2026 Cristiano Mafra Junior - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if (
                not line.analytic_distribution
                and line.contract_id.analytic_distribution
            ):
                line.analytic_distribution = line.contract_id.analytic_distribution
        return lines
