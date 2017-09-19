# -*- coding: utf-8 -*-
# Copyright 2004-2010 OpenERP SA
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2015-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts Management recurring',
    'version': '9.0.1.3.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "OpenERP SA,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    'website': 'http://openerp.com',
    'depends': ['base', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_contract.xml',
        'report/contract_views.xml',
        'data/contract_cron.xml',
        'data/contract_template.xml',
        'views/contract.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
}
