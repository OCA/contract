# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # We keep this field for migration purpose
    old_contract_id = fields.Many2one("contract.contract")

    contract_count = fields.Integer(compute="_compute_contract_count")

    def _get_related_contracts(self):
        self.ensure_one()

        contracts = self.invoice_line_ids.mapped("contract_line_id.contract_id")
        contracts |= self.old_contract_id
        return contracts

    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec._get_related_contracts())

    def action_show_contract(self):
        self.ensure_one()
        contracts = self._get_related_contracts()
        return contracts.get_formview_action()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    contract_line_id = fields.Many2one(
        "contract.line", string="Contract Line", index=True
    )
