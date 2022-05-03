# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTemplate(models.Model):
    _inherit = "contract.template"

    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Contract Sequence",
        help="This field contains the information related to the numbering "
        "of the journal entries of this journal.",
        copy=False,
        required=True,
    )
