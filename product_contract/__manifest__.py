# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Contract',
    'version': '12.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "LasLabs, "
              "ACSONE SA/NV, "
              "Odoo Community Association (OCA)",
    'website': 'https://laslabs.com',
    'depends': [
        'product',
        'contract_sale',
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'installable': True,
    'application': False,
}
