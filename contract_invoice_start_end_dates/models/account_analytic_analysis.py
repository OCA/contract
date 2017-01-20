# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from dateutil.relativedelta import relativedelta


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, fiscal_position):
        vals = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, fiscal_position)
        freq = line.analytic_account_id.recurring_rule_type
        if freq:
            start_date_str = fields.Date.context_today(self)
            start_date_dt = fields.Date.from_string(start_date_str)
            end_date_dt = start_date_dt - relativedelta(days=1)
            if freq == 'daily':
                end_date_dt += relativedelta(days=1)
            elif freq == 'weekly':
                end_date_dt += relativedelta(weeks=1)
            elif freq == 'monthly':
                end_date_dt += relativedelta(months=1)
            elif freq == 'yearly':
                end_date_dt += relativedelta(years=1)
            else:
                raise UserError(_(
                    "Contract frequence '%s' is not supported by the "
                    "module contract_start_end_dates") % freq)
            vals.update({
                'start_date': start_date_dt,
                'end_date': end_date_dt,
                })
        return vals
