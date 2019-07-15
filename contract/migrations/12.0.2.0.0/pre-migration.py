# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _set_finished_contract(cr):
    _logger.info("set recurring_next_date to false for finished contract")
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_analytic_account
        SET    recurring_next_date=NULL
        WHERE  recurring_next_date > date_end
        """,
    )


def _move_contract_recurrence_info_to_contract_line(cr):
    _logger.info("Move contract data to line level")
    openupgrade.logged_query(
        cr,
        """
    ALTER TABLE account_analytic_invoice_line
        ADD COLUMN IF NOT EXISTS recurring_rule_type         VARCHAR(255),
        ADD COLUMN IF NOT EXISTS recurring_invoicing_type    VARCHAR(255),
        ADD COLUMN IF NOT EXISTS recurring_interval          INTEGER,
        ADD COLUMN IF NOT EXISTS recurring_next_date         DATE,
        ADD COLUMN IF NOT EXISTS date_start                  DATE,
        ADD COLUMN IF NOT EXISTS date_end                    DATE
    """,
    )

    openupgrade.logged_query(
        cr,
        """
        UPDATE account_analytic_invoice_line AS contract_line
        SET
            recurring_rule_type=contract.recurring_rule_type,
            recurring_invoicing_type=contract.recurring_invoicing_type,
            recurring_interval=contract.recurring_interval,
            recurring_next_date=contract.recurring_next_date,
            date_start=contract.date_start,
            date_end=contract.date_end
        FROM
            account_analytic_account AS contract
        WHERE
            contract.id=contract_line.analytic_account_id
        """,
    )


def _move_contract_template_recurrence_info_to_contract_template_line(cr):
    _logger.info("Move contract template data to line level")
    openupgrade.logged_query(
        cr,
        """
    ALTER TABLE account_analytic_contract_line
        ADD COLUMN IF NOT EXISTS recurring_rule_type         VARCHAR(255),
        ADD COLUMN IF NOT EXISTS recurring_invoicing_type    VARCHAR(255),
        ADD COLUMN IF NOT EXISTS recurring_interval          INTEGER
    """,
    )

    openupgrade.logged_query(
        cr,
        """
    UPDATE account_analytic_contract_line AS contract_template_line
    SET
        recurring_rule_type=contract_template.recurring_rule_type,
        recurring_invoicing_type=contract_template.recurring_invoicing_type,
        recurring_interval=contract_template.recurring_interval
    FROM
        account_analytic_contract AS contract_template
    WHERE
        contract_template.id=contract_template_line.analytic_account_id
    """,
    )


@openupgrade.migrate()
def migrate(env, version):
    """
    set recurring_next_date to false for finished contract
    """
    _logger.info(">> Pre-Migration 12.0.2.0.0")
    cr = env.cr
    _set_finished_contract(cr)
    _move_contract_recurrence_info_to_contract_line(cr)
    _move_contract_template_recurrence_info_to_contract_template_line(cr)
