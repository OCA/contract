# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade

tables_to_rename = [
    (
        "agreement_rebate_settlement_line_account_invoice_line_rel",
        "ou_agreement_rebate_settlement_line_account_move_line_rel",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, tables_to_rename)
    openupgrade.remove_tables_fks(env.cr, [tables_to_rename[0][1]])
    openupgrade.rename_columns(
        env.cr, {"agreement_rebate_settlement": [("invoice_id", None)]}
    )
