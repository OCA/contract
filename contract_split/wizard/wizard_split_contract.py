# Copyright 2023 Damien Crier - Foodles
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SplitContract(models.TransientModel):
    _name = "split.contract"

    split_line_ids = fields.One2many(
        comodel_name="split.contract.line", inverse_name="split_contract_id"
    )
    main_contract_id = fields.Many2one(comodel_name="contract.contract")
    partner_id = fields.Many2one(comodel_name="res.partner")
    invoice_partner_id = fields.Many2one(comodel_name="res.partner")

    @api.model
    def default_get(self, fields) -> dict:
        vals = super().default_get(fields)
        contract_id = self.env.context.get("active_id")
        contract = self.env["contract.contract"].browse(contract_id)
        vals.update(self._get_default_values_from_contract(contract))
        return vals

    def _get_default_values_from_contract(self, contract) -> dict:
        return {
            "main_contract_id": contract.id,
            "partner_id": contract.partner_id.id,
            "invoice_partner_id": contract.invoice_partner_id.id,
            "split_line_ids": [
                (0, 0, self._get_default_split_line_values(line))
                for line in contract.contract_line_ids
            ],
        }

    def _get_default_split_line_values(self, line) -> list:
        return {
            "original_contract_line_id": line.id,
        }

    def _get_contract_name(self):
        return self.main_contract_id.name

    def _get_values_create_contract(self):
        self.ensure_one()
        return {
            "name": self._get_contract_name(),
            "partner_id": self.partner_id.id,
            "invoice_partner_id": self.invoice_partner_id.id,
            "original_contract_id": self.main_contract_id.id,
            "line_recurrence": True,
        }

    def action_split_contract(self):
        """
        If lines exists in the wizard, create a new contract <CONTRACT>
        For all lines that are kept in the wizard lines :
            - check if it needs to be split or only moved to the new contract <CONTRACT>
                - if original_qty == qty_to_split: just move the contract_id
                - if original_qty < qty_to_split: split the line
                    (eg: duplicate and change qties)
                - if qty_to_split == 0: do nothing
        """
        self.ensure_one()
        if self.split_line_ids and any(
            line.quantity_to_split for line in self.split_line_ids
        ):
            new_contract = self.env["contract.contract"].create(
                self._get_values_create_contract()
            )
            # TODO: play onchange on partner_id. use onchange_helper from OCA ?
            for line in self.split_line_ids:
                original_line = line.original_contract_line_id
                if not line.quantity_to_split:
                    continue
                if (
                    float_compare(
                        line.quantity_to_split, line.original_qty, precision_digits=2
                    )
                    == 0
                ):
                    # only move because new_qty = original_qty
                    original_line.write(
                        line._get_write_values_when_moving_line(new_contract)
                    )
                elif (
                    float_compare(
                        line.quantity_to_split, line.original_qty, precision_digits=2
                    )
                    < 0
                ):
                    # need to split and move
                    new_line = original_line.copy()
                    new_line.write(
                        line._get_write_values_when_splitting_and_moving_line(
                            new_contract, line
                        )
                    )

                    original_line.quantity -= new_line.quantity
            return new_contract
        return True


class SplitContractLine(models.TransientModel):
    _name = "split.contract.line"

    split_contract_id = fields.Many2one(comodel_name="split.contract")
    original_contract_line_id = fields.Many2one(comodel_name="contract.line")
    original_qty = fields.Float(
        related="original_contract_line_id.quantity",
        readonly=True,
        store=False,
    )
    original_contract_id = fields.Many2one(
        comodel_name="contract.contract",
        related="original_contract_line_id.contract_id",
        readonly=True,
        store=False,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="original_contract_line_id.product_id",
        readonly=True,
        store=False,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="original_contract_line_id.uom_id",
        readonly=True,
        store=False,
    )
    name = fields.Text(
        comodel_name="product.product",
        related="original_contract_line_id.name",
        readonly=True,
    )
    quantity_to_split = fields.Float(string="Quantity to move", default=0)

    @api.constrains("quantity_to_split")
    def _check_quantity_to_move(self):
        for rec in self:
            if (
                float_compare(
                    rec.quantity_to_split, rec.original_qty, precision_digits=2
                )
                > 0
            ):
                # we try to move more qty than present in the initial contract line
                raise ValidationError(
                    _(
                        "You cannot split more quantities than the "
                        "original quantity of the initial contract line."
                    )
                )

    def _get_write_values_when_moving_line(self, new_contract):
        return {
            "contract_id": new_contract.id,
            "splitted_from_contract_id": self.original_contract_id.id,
        }

    def _get_write_values_when_splitting_and_moving_line(self, new_contract, line):
        return {
            "contract_id": new_contract.id,
            "splitted_from_contract_id": self.original_contract_id.id,
            "splitted_from_line_id": self.original_contract_line_id.id,
            "quantity": line.quantity_to_split,
        }
