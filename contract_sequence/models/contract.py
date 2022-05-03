# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    name = fields.Char(
        required=True,
        default="/",
        tracking=True,
        help="Set to '/' and save if you want a new internal reference "
        "to be proposed.",
        copy="False",
    )

    def get_default_sequence(self):
        return self.env.company.contract_default_sequence

    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Contract Sequence",
        help="This field contains the information related to the numbering "
        "of the journal entries of this journal.",
        copy=False,
        default=get_default_sequence,
    )

    @api.model
    def create(self, vals):
        if "name" not in vals or vals["name"] == "/":
            sequence = (
                self.sequence_id
                or self.template_id.sequence_id
                or self.env.company.contract_default_sequence
            )
            sequence = self.env.company.contract_default_sequence
            vals["name"] = sequence.next_by_id()
        return super().create(vals)

    def write(self, vals):
        """To assign new sequence, write '/' on the name field."""
        if vals.get("name", "") == "/":
            for contract in self:
                sequence = (
                    contract.sequence_id
                    or contract.template_id.sequence_id
                    or self.env.company.contract_default_sequence
                )
                vals["name"] = sequence.next_by_id()
                super(ContractContract, contract).write(vals)
            return True
        return super().write(vals)
