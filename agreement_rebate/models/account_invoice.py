# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    agreement_rebate_settlement_line_ids = fields.One2many(
        comodel_name='agreement.rebate.settlement.line',
        inverse_name='invoice_line_id',
        string='Settlement lines',
    )
