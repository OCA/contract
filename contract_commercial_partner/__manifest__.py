# Copyright 2019 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Contract commercial partner',
    'summary': "Add stored related field 'Commercial Entity' on contracts",
    'version': '12.0.0.0.1',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'license': 'AGPL-3',
    'development_status': 'Alpha',
    'category': 'Sales',
    'description': """
Sister module of sale_commercial_partner

""",
    'depends': [
        'contract',
    ],
    'data': [
        'views/contract.xml',
    ],
    'installable': True,
    'application': False,
}
