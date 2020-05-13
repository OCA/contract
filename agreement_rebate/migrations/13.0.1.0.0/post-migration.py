# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade
from psycopg2 import sql


def update_sale_order_line_invoice_rel(cr):
    openupgrade.logged_query(
        cr,
        """INSERT INTO agreement_rebate_settlement_line_account_invoice_line_rel
        (invoice_line_id, settlement_line_id)
        SELECT aml.id, settlement_line_id
        FROM account_move_line aml
        JOIN ou_agreement_rebate_settlement_line_account_move_line_rel rel
            ON rel.invoice_line_id = aml.old_invoice_line_id""",
    )


def update_agreement_rebate_settlement_invoice(cr):
    openupgrade.logged_query(
        cr,
        sql.SQL(
            """UPDATE agreement_rebate_settlement ars
                SET invoice_id = ai.move_id
                FROM account_invoice ai
                WHERE ai.id = ars.{}"""
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_id"))),
    )


@openupgrade.migrate()
def migrate(env, version):
    update_sale_order_line_invoice_rel(env.cr)
    update_agreement_rebate_settlement_invoice(env.cr)
