# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """
    Update values from old previous_revision_id to predecessor_contract_line_id
    """
    if not openupgrade.column_exists(
            env.cr, 'contract_line', 'previous_revision_id'):
        return

    _logger.info("previous_revision_id to predecessor_contract_line_id")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE contract_line
        SET    predecessor_contract_line_id=previous_revision_id
        WHERE  previous_revision_id IS NOT NULL AND (
        predecessor_contract_line_id IS NULL OR predecessor_contract_line_id=0)
        """,
    )
