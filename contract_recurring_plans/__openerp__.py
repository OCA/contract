# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Analytic plans on contracts recurring invoices',
    'version': '8.0.1.0.0',
    'category': 'Contract Management',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'account_analytic_plans',
        'account_analytic_analysis',
    ],
    'data': [
        'views/account_analytic_invoice_line_view.xml',
    ],
    'installable': True,
}
