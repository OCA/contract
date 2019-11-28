# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from dateutil.relativedelta import relativedelta
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Init next_period_end_date field")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        cl_model = env['contract.line']
        contract_lines = cl_model.search([])
        for cl in contract_lines:
            if cl.date_end and cl.last_date_invoiced == cl.date_end:
                continue  # Finished lines
            next_period_start_date = (
                cl.last_date_invoiced + relativedelta(days=1)
                if cl.last_date_invoiced
                else cl.date_start
            )
            cl.next_period_end_date = cl_model._get_next_period_end_date(
                next_period_start_date,
                cl.recurring_rule_type,
                cl.recurring_interval,
            )
