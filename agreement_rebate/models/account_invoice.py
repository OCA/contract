# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    agreement_rebate_settlement_line_ids = fields.Many2many(
        comodel_name="agreement.rebate.settlement.line",
        relation="agreement_rebate_settlement_line_account_invoice_line_rel",
        column1="invoice_line_id",
        column2="settlement_line_id",
        string="Settlement lines",
    )
