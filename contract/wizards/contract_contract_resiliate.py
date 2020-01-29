# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContractResiliate(models.TransientModel):

    _name = 'contract.contract.resiliate'
    _description = "Resiliate Contract Wizard"

    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=True,
        ondelete="cascade",
    )
    resiliate_reason_id = fields.Many2one(
        comodel_name="contract.resiliate.reason",
        string="Resiliate Reason",
        required=True,
        ondelete="cascade",
    )
    resiliate_comment = fields.Text(string="Resiliate Comment", required=True)
    resiliate_date = fields.Date(string="Resiliate Date", required=True)

    @api.multi
    def resiliate_contract(self):
        for wizard in self:
            wizard.contract_id._resiliate_contract(
                wizard.resiliate_reason_id,
                wizard.resiliate_comment,
                wizard.resiliate_date,
            )
        return True
