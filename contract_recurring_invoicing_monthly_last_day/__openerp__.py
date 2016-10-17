# -*- coding: utf-8 -*-
# © 2016 Binovo IT Human Project SL <elacunza@binovo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Contract recurring invoice type monthly - last day",
    'summary': '''
        Adds a new invoice recurring period for contracts - month(s) last day.
        ''',
    'author': 'Binovo IT Human Project SL - Eneko Lacunza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.binovo.es',
    'category': 'Sales Management',
    'version': '8.0.1.0.0',
    'depends': ['account_analytic_analysis'],
    'license': 'AGPL-3',
    'test': [
        'test/contract_recurring_invoicing_monthly_last_day.yml'
    ],
    'installable': True,
}
