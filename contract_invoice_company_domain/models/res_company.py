# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    create_recurring_invoices = fields.Boolean(default=True)
    contract_to_invoice_domain = fields.Char(
        help="Extra domain applied on the contracts of this company when the "
        "recurring invoices cron selects the contracts to invoice.",
    )
