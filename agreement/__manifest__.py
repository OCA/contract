# -*- coding: utf-8 -*-
{
    'name': "Agreements",
    'summary': "Manage Agreements, LOI and Contracts",
    'author': "Pavlov Media",
    'website': "https://github.com/OCA/contract",
    'category': 'Partner',
    'version': '11.0.0.0.1',
    'depends': [
        'mail',
        'sale_management'
    ],
    'data': [
        'views/reports.xml',
        'views/agreement.xml',
        'views/agreement_clause.xml',
        'views/agreement_section.xml',
        'views/agreement_stages.xml',
        'views/agreement_type.xml',
        'views/agreement_subtype.xml',
        'views/agreement_renewaltype.xml',
        'views/agreement_increasetype.xml',
        'views/res_partner.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
