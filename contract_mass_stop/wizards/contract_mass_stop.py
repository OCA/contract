# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractMassStop(models.TransientModel):

    _name = "contract.mass.stop"
    _description = "Contract Mass Stop"

    name = fields.Char()
    date_start = fields.Date(
        required=True, help="The date from which contract lines should be interrupted."
    )
    date_end = fields.Date(
        required=True, help="The date until contract lines should be interrupted."
    )
    is_auto_renew = fields.Boolean()
    contract_ids = fields.Many2many(
        comodel_name="contract.contract",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        if active_ids:
            res["contract_ids"] = [(6, 0, active_ids)]
        return res

    def stop_contracts(self):
        self.contract_ids.mapped("contract_line_ids").stop_plan_successor(
            self.date_start, self.date_end, self.is_auto_renew
        )

    def doit(self):
        for wizard in self:
            wizard.stop_contracts()
        return True
