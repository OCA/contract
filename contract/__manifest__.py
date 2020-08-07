# Copyright 2004-2010 OpenERP SA
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# Copyright 2015 Domatix
# Copyright 2016-2018 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Recurring - Contracts Management',
    'version': '12.0.7.3.3',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "OpenERP SA, "
              "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': ['base', 'account', 'product'],
    "external_dependencies": {"python": ["dateutil"]},
    'data': [
        'security/groups.xml',
        'security/contract_tag.xml',
        'security/ir.model.access.csv',
        'security/contract_security.xml',
        'security/contract_terminate_reason.xml',
        'report/report_contract.xml',
        'report/contract_views.xml',
        'data/contract_cron.xml',
        'data/contract_renew_cron.xml',
        'data/mail_template.xml',
        'data/ir_ui_menu.xml',
        'wizards/contract_line_wizard.xml',
        'wizards/contract_manually_create_invoice.xml',
        'wizards/contract_contract_terminate.xml',
        'views/contract_tag.xml',
        'views/assets.xml',
        'views/abstract_contract_line.xml',
        'views/contract.xml',
        'views/contract_line.xml',
        'views/contract_template.xml',
        'views/contract_template_line.xml',
        'views/res_partner_view.xml',
        'views/res_config_settings.xml',
        'views/contract_terminate_reason.xml',
    ],
    'installable': True,
}
