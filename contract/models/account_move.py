# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # We keep this field for migration purpose
    old_contract_id = fields.Many2one("contract.contract")
