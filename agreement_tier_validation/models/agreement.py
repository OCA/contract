# Copyright 2022 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _name = "agreement"
    _inherit = ["agreement", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["active"]

    _tier_validation_manual_config = False

    hide_active_button = fields.Boolean(
        compute="_compute_hide_active_button", readonly=True
    )

    @api.depends("need_validation")
    def _compute_hide_active_button(self):
        for rec in self:
            rec.hide_active_button = (
                rec.need_validation
                or rec.state not in ("draft")
                or (rec.review_ids and not rec.validated)
                or rec.is_template
            )

    def make_active(self):
        self.state = "active"
