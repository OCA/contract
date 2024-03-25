# Copyright 2019-2020 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    auto_post = fields.Selection(
        string="Auto-post",
        selection=[
            ("no", "No"),
            ("at_date", "At Date"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        default="no",
        required=True,
        copy=False,
        help="Specify whether this entry is posted automatically on its accounting date,"
        " and any similar recurring invoices.",
    )

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super()._prepare_invoice(
            date_invoice=date_invoice, journal=journal
        )
        invoice_vals.update({"auto_post": self.auto_post})
        return invoice_vals
