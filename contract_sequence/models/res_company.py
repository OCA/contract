# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    contract_default_sequence = fields.Many2one(
        "ir.sequence",
        string="Default sequence",
        default=lambda self: self.env['ir.model.data'].xmlid_to_res_id(
            'contract_sequence.seq_contract_auto')
    )
