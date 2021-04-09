# Copyright 2020-2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET old_contract_id = ai.old_contract_id
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id
            AND ai.old_contract_id IS NOT NULL""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET contract_line_id = ail.contract_line_id
        FROM account_invoice_line ail
        WHERE ail.id = aml.old_invoice_line_id
            AND ail.contract_line_id IS NOT NULL""",
    )
    openupgrade.load_data(
        env.cr, "contract", "migrations/13.0.1.0.0/noupdate_changes.xml"
    )
    # Don't alter line recurrence v12 behavior
    openupgrade.logged_query(
        env.cr, "UPDATE contract_contract SET line_recurrence = True",
    )
