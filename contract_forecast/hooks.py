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
        offset = 0
        while True:
            contract_lines = env["contract.line"].search(
                [('is_canceled', '=', False)], limit=100, offset=offset
            )
            contract_lines.with_delay()._generate_forecast_periods()
            if len(contract_lines) < 100:
                break
            offset += 100
