# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    agreement_ids = fields.One2many("agreement", "partner_id", string="Agreements")
