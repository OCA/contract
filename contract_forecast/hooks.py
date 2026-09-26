# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Generate contract line forecast periods"""
    _logger.info(
        "Post init hook for module contract_forecast: "
        "Generate contract line forecast periods"
    )
    offset = 0
    while True:
        contract_lines = env["contract.line"].search(
            [("is_canceled", "=", False)], limit=100, offset=offset
        )
        contract_lines.with_delay()._generate_forecast_periods()
        if len(contract_lines) < 100:
            break
        offset += 100
