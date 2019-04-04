# -*- coding: utf-8 -*-
# Copyright 2019 - Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        vals = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, invoice_id)
        if line.product_id.must_have_dates:
            vals.update({
                'start_date': self.env.context['date_from'],
                'end_date': self.env.context['date_to'],
            })
        return vals
