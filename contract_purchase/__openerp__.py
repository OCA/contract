# -*- coding: utf-8 -*-
# © Stefan Becker <s.becker@humanilog.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Contract',
    'summary': 'Create purchase contract',
    'version': '9.0.1.0.0',
    'author': "humanilog, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.humanilog.org/',
    'depends': ['contract', 'purchase'],
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'data': [
        'views/contract_view.xml',
    ],
    'installable': True,
}
