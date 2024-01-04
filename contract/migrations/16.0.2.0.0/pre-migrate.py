# © 2023 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Migrate analytic account from contract line to analytic distribution"""

    _logger.info("Migrating analytic distribution for contract.line")
    cr.execute(
        """
            SELECT id, analytic_account_id, analytic_distribution
            FROM contract_line
            WHERE analytic_account_id IS NOT NULL
        """
    )
    for line_id, analytic_account_id, analytic_distribution in cr.fetchall():
        analytic_account_id = str(analytic_account_id)
        if analytic_distribution:
            analytic_distribution[analytic_account_id] = (
                analytic_distribution.get(analytic_account_id, 0) + 100
            )
        else:
            analytic_distribution = {analytic_account_id: 100}

        cr.execute(
            "UPDATE contract_line SET analytic_distribution = %s WHERE id = %s",
            (json.dumps(analytic_distribution), line_id),
        )
