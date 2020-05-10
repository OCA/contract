# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # We keep this field for migration purpose
    old_contract_id = fields.Many2one('contract.contract', oldname='contract_id')

    def create(self, values):
        """
            Create a new record for a model AccountInvoice
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        print(values)
        result = super(AccountInvoice, self).create(values)
    
        return result
    
