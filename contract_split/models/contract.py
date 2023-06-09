# Copyright 2023 Damien Crier - Foodles
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    original_contract_id = fields.Many2one(
        comodel_name="contract.contract",
        readonly=True,
    )


class ContractLine(models.Model):
    _inherit = "contract.line"

    splitted_from_line_id = fields.Many2one(
        comodel_name="contract.line",
        readonly=True,
    )
    splitted_from_contract_id = fields.Many2one(
        comodel_name="contract.contract",
        readonly=True,
    )
