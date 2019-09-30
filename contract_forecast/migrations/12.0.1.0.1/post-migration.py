# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Set company_id for all forecasts"""
    _logger.info("Set company_id for all forecasts")
    cr.execute("""
    UPDATE contract_line_forecast_period AS forecast
    SET company_id=contract.company_id
    FROM contract_contract AS contract
    WHERE forecast.contract_id=contract.id
    AND forecast.contract_id IS NOT NULL
    """)
