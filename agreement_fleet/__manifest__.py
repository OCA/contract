# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement Fleet',
    'summary': """
        Link fleet vehicles to an agreement""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'maintainers': ['marcelsavegnago'],
    'images': ['static/description/banner.png'],
    'website': 'https://github.com/oca/contract',
    'category': 'Contract',
    'depends': [
        'fleet',
        'agreement_serviceprofile',
    ],
    'data': [
        'views/fleet_vehicle.xml',
        'views/agreement.xml',
    ],
}
