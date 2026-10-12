# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from random import randint

from odoo import fields, models


class ContractTag(models.Model):
    _name = "contract.tag"
    _description = "Contract Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    color = fields.Integer(
        string="Color Index", default=lambda self: self._get_default_color()
    )
