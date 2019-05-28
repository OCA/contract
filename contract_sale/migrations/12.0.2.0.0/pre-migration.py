# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    xmlids_to_rename = [
        ('contract_sale.account_analytic_account_own_salesman',
         'contract_sale.contract_contract_own_salesman'),
        ('contract_sale.account_analytic_account_see_all',
         'contract_sale.contract_contract_see_all'),
        ('contract_sale.account_analytic_contract_salesman',
         'contract_sale.contract_template_salesman'),
        ('contract_sale.account_analytic_contract_sale_manager',
         'contract_sale.contract_template_sale_manager'),
        ('contract_sale.account_analytic_invoice_line_saleman',
         'contract_sale.contract_line_saleman'),
        ('contract_sale.account_analytic_invoice_line_manager',
         'contract_sale.contract_line_manager'),
        ('contract_sale.account_analytic_contract_line_salesman',
         'contract_sale.contract_template_line_salesman'),
        ('contract_sale.account_analytic_contract_line_manager',
         'contract_sale.contract_template_line_manager'),
        ('contract_sale.account_analytic_account_contract_salesman',
         'contract_sale.contract_contract_salesman'),
    ]
    openupgrade.rename_xmlids(cr, xmlids_to_rename)
