# -*- coding: utf-8 -*-
# Copyright 2019 - Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    contract_pregenerate_days = fields.Integer(
        string='Days to prepare invoices',
        help="Days before next invoice date to generate draft invoices.\n"
             "This allows users to check the invoices before confirmation,\n"
             " and to send invoices to customers, before the invoice date.")
