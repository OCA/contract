# -*- coding: utf-8 -*-
# Copyright 2004-2010 OpenERP SA
# Copyright 2014-2017 Tecnativa - Pedro M. Baeza
# Copyright 2015 Domatix
# Copyright 2016-2017 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts Management - Recurring',
    'version': '10.0.4.2.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "OpenERP SA, "
              "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': ['base', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'security/contract_security.xml',
        'report/report_contract.xml',
        'report/contract_views.xml',
        'data/contract_cron.xml',
        'data/mail_template.xml',
        'views/account_analytic_account_view.xml',
        'views/account_analytic_contract_view.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
}
