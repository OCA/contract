# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    @api.multi
    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super()._prepare_invoice(date_invoice, journal=journal)
        if self.transmit_method_id:
            invoice_vals["transmit_method_id"] = self.transmit_method_id.id
        return invoice_vals
