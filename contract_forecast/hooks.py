# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api
from odoo.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Generate contract line forecast periods
    """
    _logger.info(
        "Post init hook for module post_init_hook: "
        "Generate contract line forecast periods"
    )
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        contract_lines = env["account.analytic.invoice.line"].search(
            [('is_canceled', '=', False)]
        )
        for contract_line in contract_lines:
            contract_line.with_delay()._generate_forecast_periods()
