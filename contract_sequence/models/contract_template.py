# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ContractTemplate(models.Model):
    _inherit = "contract.template"

    def get_default_sequence(self):
        result = self.env.company.contract_default_sequence or self.env.ref(
            "contract_sequence.seq_contract_auto"
        )
        if not result:
            raise UserWarning(_("No default sequence found!"))
        return result

    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Contract Sequence",
        help="This field contains the information related to the numbering "
        "of the journal entries of this journal.",
        copy=False,
        required=True,
        default=get_default_sequence,
    )

    @api.model
    def create(self, vals):
        if "name" not in vals or vals["name"] == "/":
            sequence = self.sequence_id or self.get_default_sequence()
            vals["name"] = sequence.next_by_id()
        return super().create(vals)
