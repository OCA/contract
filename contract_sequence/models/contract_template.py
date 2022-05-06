# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTemplate(models.Model):
    _inherit = "contract.template"

    def get_default_sequence(self):
        return (
            self.env.company.contract_default_sequence
            or self.env.company.get_default_contract_sequence()
        )

    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Contract Sequence",
        help="This field contains the information related to the numbering "
        "of the journal entries of this journal.",
        copy=False,
        required=True,
        default=get_default_sequence,
    )
