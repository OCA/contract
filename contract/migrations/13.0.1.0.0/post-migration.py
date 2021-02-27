# Copyright 2020-2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "contract", "migrations/13.0.1.0.0/noupdate_changes.xml"
    )
    # Don't alter line recurrence v12 behavior
    contracts = env["contract.contract"].search([])
    contracts.write({"line_recurrence": True})
