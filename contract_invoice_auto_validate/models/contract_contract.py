# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    def _finalize_and_create_invoices(self, invoices_values):
        invoices = super()._finalize_and_create_invoices(invoices_values)
        invoices.filtered("invoice_line_ids").action_invoice_open()
        return invoices
