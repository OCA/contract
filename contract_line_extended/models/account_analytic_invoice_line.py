# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    partner_id = fields.Many2one(
        related='analytic_account_id.partner_id',
        store=True,
        readonly=True)
    date_start = fields.Date(
        related='analytic_account_id.date_start',
        store=True,
        readonly=True)
    date_end = fields.Date(
        related='analytic_account_id.date_end',
        store=True,
        readonly=True)
