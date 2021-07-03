# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2020 Technolibre - Carms Ng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = ['contract.contract']

    customer_signature = fields.Binary(
        string='Customer acceptance',
        attachment=True
    )
    signature_name = fields.Char(
        string='Signed by',
    )

    @api.model
    def create(self, values):
        contract = super(ContractContract, self).create(values)
        if contract.customer_signature:
            values = {'customer_signature': contract.customer_signature}
            contract._track_signature(values, 'customer_signature')
        return contract

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(ContractContract, self).write(values)
