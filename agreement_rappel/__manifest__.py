# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Agreement Rappel',
    'summary': 'rappel in agreements',
    'version': '12.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Contract',
    'website': 'https://github.com/OCA/contract',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'account',
        'agreement',
    ],
    'data': [
        'data/agreement_rappel_data.xml',
        'security/agreement_security.xml',
        'security/ir.model.access.csv',
        'views/agreement_type_view.xml',
        'views/agreement_view.xml',
        'views/settlement_view.xml',
        'wizards/invoice_create_views.xml',
        'wizards/settlement_create_views.xml',
    ],
}
