# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    repair_count = fields.Integer("# Repair Orders", compute="_compute_repair_count")

    def _compute_repair_count(self):
        for ag_rec in self:
            ag_rec.repair_count = self.env["repair.order"].search_count(
                [("agreement_id", "in", ag_rec.ids)]
            )
