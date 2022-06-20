# Copyright 2022 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Agreement(models.Model):
    _name = "agreement"
    _inherit = ["agreement", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["active"]

    _tier_validation_manual_config = False
