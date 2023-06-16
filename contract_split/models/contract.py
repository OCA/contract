# Copyright 2023 Damien Crier - Foodles
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    original_contract_ids = fields.Many2many(
        comodel_name="contract.contract",
        relation="contract_split_contract_rel",
        column1="contract_id",
        column2="split_contract_id",
        readonly=True,
    )

    @api.model
    def _get_contract_split_name(self, split_wizard):
        return split_wizard.main_contract_id.name

    @api.model
    def _get_values_create_split_contract(self, split_wizard):
        return {
            "name": self._get_contract_split_name(split_wizard),
            "partner_id": split_wizard.partner_id.id,
            "invoice_partner_id": split_wizard.invoice_partner_id.id,
            "original_contract_ids": [split_wizard.main_contract_id.id],
            "line_recurrence": True,
        }

    def _get_default_split_values(self) -> dict:
        self.ensure_one()
        return {
            "main_contract_id": self.id,
            "partner_id": self.partner_id.id,
            "invoice_partner_id": self.invoice_partner_id.id,
            "split_line_ids": [
                (0, 0, line._get_default_split_line_values())
                for line in self.contract_line_ids
            ],
        }


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

    def _get_write_values_when_moving_line(self, new_contract):
        self.ensure_one()
        return {
            "contract_id": new_contract.id,
            "splitted_from_contract_id": self.contract_id.id,
        }

    def _get_write_values_when_splitting_and_moving_line(self, new_contract, qty):
        self.ensure_one()
        return {
            "contract_id": new_contract.id,
            "splitted_from_contract_id": self.contract_id.id,
            "splitted_from_line_id": self.id,
            "quantity": qty,
        }

    def _get_default_split_line_values(self) -> dict:
        self.ensure_one()
        return {
            "original_contract_line_id": self.id,
            "quantity_to_split": self.quantity,
        }
