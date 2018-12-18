# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    contract_id = fields.Many2one(
        'account.analytic.account', string='Contract'
    )

    @api.multi
    def finalize_creation_from_contract(self):
        for invoice in self:
            invoice._onchange_partner_id()
        self.compute_taxes()
