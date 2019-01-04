# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    set recurring_next_date to false for finished contract
    """
    _logger.info("order all contract line")
    with api.Environment(cr, SUPERUSER_ID, {}) as env:
        contracts = env["account.analytic.account"].search([])
        finished_contract = contracts.filtered(
            lambda c: not c.create_invoice_visibility
        )
        cr.execute(
            "UPDATE account_analytic_account set recurring_next_date=null "
            "where id in (%)" % ','.join(finished_contract.ids)
        )
