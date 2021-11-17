# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    agreement_ids = fields.One2many("agreement", "partner_id", string="Agreements")
    agreements_count = fields.Integer(compute="_compute_agreements_count")

    @api.depends("agreement_ids")
    def _compute_agreements_count(self):
        for record in self:
            record.agreements_count = len(record.agreement_ids)

    def action_open_agreement(self):
        self.ensure_one()
        action = self.env.ref("agreement.agreement_action")
        result = action.read()[0]
        result["domain"] = [("partner_id", "=", self.id)]
        result["context"] = {
            "default_partner_id": self.id,
        }
        return result
