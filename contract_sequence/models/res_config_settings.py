# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contract_default_sequence = fields.Many2one(
        related="company_id.contract_default_sequence",
        string="Default sequence",
        readonly=False,
    )

    @api.onchange("company_id")
    def onchange_company_id(self):
        if self.company_id:
            if not self.contract_default_sequence:
                self.contract_default_sequence = self.env.ref(
                    "contract_sequence.seq_contract_auto"
                ).id
