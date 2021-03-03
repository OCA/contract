# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    agreement_id = fields.Many2one(
        comodel_name="agreement",
        string="Agreement",
        ondelete="restrict",
    )

    @api.constrains("agreement_id", "active")
    def _check_contract(self):
        contracts = self.search([("agreement_id", "=", self.agreement_id.id)])
        if self.agreement_id and len(contracts) > 1:
            raise UserError(
                _(
                    "Contract related with agreement '%s' must have only one contract."
                    % (self.agreement_id.name,)
                )
            )
