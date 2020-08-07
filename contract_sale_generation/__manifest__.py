# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)


{
    'name': 'Contracts Management - Recurring Sales',
    'version': '12.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "PESOL, Okia, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': ['contract', 
                'sale',
                'sale_timesheet',
                'sale_invoice_group_method',
                'contract_sale_mandate',
                'product_contract',
#                 'agreement_sale',
                ],
    'data': [
        'views/contract_contract_view.xml',
        'views/sale_view.xml',
        'views/contract_template.xml',
        'data/contract_cron.xml',
    ],
    'installable': True,
}
