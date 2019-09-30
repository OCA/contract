# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    xmlids_to_rename = [
        (
            'product_contract.account_analytic_account_recurring_form_form',
            'product_contract.contract_contract_customer_form_view',
        )
    ]
    openupgrade.rename_xmlids(cr, xmlids_to_rename)
