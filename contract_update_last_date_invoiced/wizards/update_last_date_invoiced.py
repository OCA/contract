# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PrgEditLastDateInvoicedWizard(models.TransientModel):

    _name = "contract.update.last.date.invoiced"
    _description = "Update Contract Last Date Invoiced Wizard"

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line",
        required=True,
        ondelete="cascade",
    )
    last_date_invoiced = fields.Date()
    recurring_next_date = fields.Date()

    def update_last_date_invoiced(self):
        for wizard in self:
            wizard.contract_line_id._update_last_date_invoiced(
                wizard.last_date_invoiced, wizard.recurring_next_date
            )
        return True
