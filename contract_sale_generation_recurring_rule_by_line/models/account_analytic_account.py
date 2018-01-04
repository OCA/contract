# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def update_sale_date(self, old_date, new_date):
        self.ensure_one()
        if self.type == 'sale':
            recurring_lines = self.mapped(
                    'recurring_invoice_line_ids').filtered(
                lambda l: fields.Date.from_string(
                    l.recurring_next_date) == old_date
            )
            recurring_lines.update_date()

    @api.multi
    def update_date(self, old_date, new_date):
        self.ensure_one()
        if self.type == 'invoice':
            recurring_lines = self.mapped(
                    'recurring_invoice_line_ids').filtered(
                lambda l: fields.Date.from_string(
                    l.recurring_next_date) == old_date
            )
            recurring_lines.update_date()
