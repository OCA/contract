# Copyright 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement Helpdesk Mgmt',
    'summary': """
            Link a helpdesk ticket to an agreement""",
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/contract',
    'images': ['static/description/banner.png'],
    'depends': [
        "helpdesk_mgmt",
        "agreement_serviceprofile",
    ],
    'data': [
        'views/helpdesk_ticket.xml',
        'views/agreement.xml',
    ],
    'maintainers': [
        'bodedra'
    ],
}
