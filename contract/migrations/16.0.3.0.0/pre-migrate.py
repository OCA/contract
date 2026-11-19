# Copyright ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Fill in date (signature date) on existing contracts"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Fill in date (signature date) on existing contracts")
    fields_spec = [
        ("date", "contract.contract", "contract_contract", "date", "contract")
    ]
    openupgrade.add_fields(env, fields_spec)

    cr.execute(
        """
            UPDATE contract_contract
                SET date =
                    CASE
                        WHEN date_start IS NOT NULL THEN date_start
                        ELSE create_date
                        END
        """
    )
