# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    free_invoice_date = fields.Boolean(string="Free Invoice Date")

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super(ContractContract, self)._prepare_invoice(
            date_invoice, journal
        )
        invoice_vals.update(
            {"invoice_date": not self.free_invoice_date and date_invoice}
        )
        return invoice_vals, move_form
