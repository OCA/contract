# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # We keep this field for migration purpose
    old_contract_id = fields.Many2one(
        'contract.contract', oldname='contract_id')
