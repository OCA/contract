# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contract Line Invoice By Average',
    'version': '12.0.1.0.0',
    'category': 'Contract',
    'summary': "Contract Line Invoice By Average.",
    'author': 'Open Source Integrators, '
			  'Serpent Consulting Services Pvt. Ltd.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/contract',
    'depends': [
        'account_invoice_pricelist',
        'contract_sale_invoicing',
        'product_contract'
    ],
    'data': [
        'views/contract_line_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
