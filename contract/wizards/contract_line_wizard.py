# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticInvoiceLineWizard(models.TransientModel):

    _name = 'account.analytic.invoice.line.wizard'
    _description = 'Contract Line Wizard'

    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    recurring_next_date = fields.Date(string='Next Invoice Date')
    is_auto_renew = fields.Boolean(string="Auto Renew", default=False)
    is_suspended = fields.Boolean(string="Is a suspension", default=False)
    contract_line_id = fields.Many2one(
        comodel_name="account.analytic.invoice.line",
        string="Contract Line",
        required=True,
        index=True,
    )

    @api.multi
    def stop(self):
        for wizard in self:
            wizard.contract_line_id.stop(
                wizard.date_end, is_suspended=wizard.is_suspended
            )
        return True

    @api.multi
    def plan_successor(self):
        for wizard in self:
            wizard.contract_line_id.plan_successor(
                wizard.date_start, wizard.date_end, wizard.is_auto_renew
            )
        return True

    @api.multi
    def stop_plan_successor(self):
        for wizard in self:
            wizard.contract_line_id.stop_plan_successor(
                wizard.date_start, wizard.date_end, wizard.is_auto_renew
            )
        return True

    @api.multi
    def uncancel(self):
        for wizard in self:
            wizard.contract_line_id.uncancel(wizard.recurring_next_date)
        return True
