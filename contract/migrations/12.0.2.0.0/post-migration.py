# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Copy recurrence info from contract to contract lines and compute
    last_date_invoiced"""

    cr.execute(
        """UPDATE account_analytic_invoice_line AS contract_line
        SET recurring_rule_type=contract.recurring_rule_type,
        recurring_invoicing_type=contract.recurring_invoicing_type,
        recurring_interval=contract.recurring_interval,
        recurring_next_date=contract.recurring_next_date,
        date_start=contract.date_start,
        date_end=contract.date_end
        FROM account_analytic_account AS contract
        WHERE contract.id=contract_line.contract_id"""
    )

    _logger.info("order all contract line")
    env = api.Environment(cr, SUPERUSER_ID, {})
    contract_lines = env["account.analytic.invoice.line"].search(
        [("recurring_next_date", "!=", False)]
    )
    contract_lines._init_last_date_invoiced()
