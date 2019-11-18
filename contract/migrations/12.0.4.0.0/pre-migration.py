# Copyright 2019 ACSONE SA/NV
# Copyright 2019 Tecnativa 2019 - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade
from psycopg2 import sql

_logger = logging.getLogger(__name__)

models_to_rename = [
    # Contract Line Wizard
    ('account.analytic.invoice.line.wizard', 'contract.line.wizard'),
    # Abstract Contract
    ('account.abstract.analytic.contract', 'contract.abstract.contract'),
    # Abstract Contract Line
    (
        'account.abstract.analytic.contract.line',
        'contract.abstract.contract.line',
    ),
    # Contract Line
    ('account.analytic.invoice.line', 'contract.line'),
    # Contract Template
    ('account.analytic.contract', 'contract.template'),
    # Contract Template Line
    ('account.analytic.contract.line', 'contract.template.line'),
]
tables_to_rename = [
    # Contract Line
    ('account_analytic_invoice_line', 'contract_line'),
    # Contract Template
    ('account_analytic_contract', 'contract_template'),
    # Contract Template Line
    ('account_analytic_contract_line', 'contract_template_line'),
]
columns_to_copy = {
    'contract_line': [
        ('analytic_account_id', 'contract_id', None),
    ],
}
xmlids_to_rename = [
    (
        'contract.account_analytic_cron_for_invoice',
        'contract.contract_cron_for_invoice',
    ),
    (
        'contract.account_analytic_contract_manager',
        'contract.contract_template_manager',
    ),
    (
        'contract.account_analytic_contract_user',
        'contract.contract_template_user',
    ),
    (
        'contract.account_analytic_invoice_line_manager',
        'contract.contract_line_manager',
    ),
    (
        'contract.account_analytic_invoice_line_user',
        'contract.contract_line_user',
    ),
    (
        'contract.account_analytic_contract_line_manager',
        'contract.contract_template_line_manager',
    ),
    (
        'contract.account_analytic_contract_line_user',
        'contract.contract_template_line_user',
    ),
]


def _get_contract_field_name(cr):
    """
    Contract field changed the name from analytic_account_id to contract_id
    in 12.0.2.0.0. This method used to get the contract field name in
    account_analytic_invoice_line"""
    return (
        'contract_id'
        if openupgrade.column_exists(
            cr, 'account_analytic_invoice_line', 'contract_id'
        )
        else 'analytic_account_id'
    )


def create_contract_records(cr):
    contract_field_name = _get_contract_field_name(cr)
    openupgrade.logged_query(
        cr, """
        CREATE TABLE contract_contract
        (LIKE account_analytic_account INCLUDING ALL)""",
    )
    openupgrade.logged_query(
        cr, sql.SQL("""
        INSERT INTO contract_contract
        SELECT * FROM account_analytic_account
        WHERE id IN (SELECT DISTINCT {} FROM contract_line)
        """).format(
            sql.Identifier(contract_field_name),
        ),
    )
    # Deactivate disabled contracts
    openupgrade.logged_query(
        cr, """UPDATE contract_contract cc
        SET active = False
        FROM account_analytic_account aaa
        WHERE aaa.id = cc.id
            AND NOT aaa.recurring_invoices""",
    )
    # Handle id sequence
    cr.execute("CREATE SEQUENCE IF NOT EXISTS contract_contract_id_seq")
    cr.execute("SELECT setval('contract_contract_id_seq', "
               "(SELECT MAX(id) FROM contract_contract))")
    cr.execute("ALTER TABLE contract_contract ALTER id "
               "SET DEFAULT NEXTVAL('contract_contract_id_seq')")
    # Move common stuff from one table to the other
    mapping = [
        ('ir_attachment', 'res_model', 'res_id'),
        ('mail_message', 'model', 'res_id'),
        ('mail_activity', 'res_model', 'res_id'),
        ('mail_followers', 'res_model', 'res_id'),
    ]
    for table, model_column, id_column in mapping:
        openupgrade.logged_query(
            cr, sql.SQL("""
            UPDATE {table} SET {model_column}='contract.contract'
            WHERE {model_column}='account.analytic.account'
                AND {id_column} IN (SELECT DISTINCT {col} FROM contract_line)
            """).format(
                table=sql.Identifier(table),
                model_column=sql.Identifier(model_column),
                id_column=sql.Identifier(id_column),
                col=sql.Identifier(contract_field_name),
            ),
        )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_models(cr, models_to_rename)
    openupgrade.rename_tables(cr, tables_to_rename)
    openupgrade.rename_xmlids(cr, xmlids_to_rename)
    openupgrade.copy_columns(cr, columns_to_copy)
    create_contract_records(cr)
