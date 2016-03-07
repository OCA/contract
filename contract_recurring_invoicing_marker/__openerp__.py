# -*- coding: utf-8 -*-
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Markers for contract recurring invoices',
    'version': '8.0.1.0.0',
    'category': 'Contract Management',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'account_analytic_analysis',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/account_analytic_account_view.xml',
    ],
    'installable': True,
}
