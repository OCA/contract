# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    create_recurring_invoices = fields.Boolean(
        related="company_id.create_recurring_invoices", readonly=False
    )
    contract_to_invoice_domain = fields.Char(
        related="company_id.contract_to_invoice_domain", readonly=False
    )

    @api.onchange("create_recurring_invoices")
    def _onchange_create_recurring_invoices(self):
        if not self.create_recurring_invoices:
            self.contract_to_invoice_domain = False
