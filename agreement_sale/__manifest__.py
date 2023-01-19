# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement Sale',
    'summary': "Agreement on sales",
    'version': '12.0.1.0.2',
    'category': 'Contract',
    'author': 'Akretion, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'license': 'AGPL-3',
    'depends': [
        'sale_management',
        'agreement_account',
        'sale_commercial_partner',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/agreement.xml',
        'views/sale_order.xml',
        'views/res_config_settings.xml',
        ],
    'development_status': 'Beta',
    'maintainers': [
        'alexis-via',
        'bealdav',
    ],
    'installable': True,
}
