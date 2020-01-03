# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """
    set recurring_next_date to false for finished contract
    """
    _logger.info(">> Pre-Migration 12.0.1.0.0")
    cr = env.cr
    