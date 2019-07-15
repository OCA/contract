# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade
from odoo.tools import parse_version

_logger = logging.getLogger(__name__)

CONTRACT_FIELDS = [
    'id',
    'name',
    'partner_id',
    'pricelist_id',
    'contract_type',
    'journal_id',
    'company_id',
    'active',
    'code',
    'group_id',
    'contract_template_id',
    'user_id',
    'recurring_next_date',
    'date_end',
    'message_main_attachment_id',
    'create_uid',
    'create_date',
    'write_uid',
    'write_date',
    'payment_term_id',
    'fiscal_position_id',
    'invoice_partner_id',
]

CONTRACT_LINE_FIELDS = [
    'id',
    'product_id',
    'name',
    'quantity',
    'uom_id',
    'automatic_price',
    'specific_price',
    'discount',
    'recurring_rule_type',
    'recurring_invoicing_type',
    'recurring_interval',
    'sequence',
    'date_start',
    'date_end',
    'recurring_next_date',
    'last_date_invoiced',
    'termination_notice_date',
    'successor_contract_line_id',
    'predecessor_contract_line_id',
    'manual_renew_needed',
    'create_uid',
    'create_date',
    'write_uid',
    'write_date',
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


def _copy_contract_table(cr):
    contract_fields = []
    for field in CONTRACT_FIELDS:
        if openupgrade.column_exists(cr, 'account_analytic_account', field):
            contract_fields.append(field)
    contract_field_name = _get_contract_field_name(cr)
    openupgrade.logged_query(
        cr,
        "INSERT INTO contract_contract ("
        + ', '.join(contract_fields)
        + ") "
        + "SELECT "
        + ', '.join(contract_fields)
        + " FROM account_analytic_account "
        + "WHERE id in ( SELECT DISTINCT "
        + contract_field_name
        + " FROM "
        + "account_analytic_invoice_line)",
    )
    if openupgrade.column_exists(cr, 'account_invoice', 'old_contract_id_tmp'):
        openupgrade.logged_query(
            cr,
            """
            UPDATE account_invoice
            SET old_contract_id = old_contract_id_tmp
            """,
        )

    # Move contract attachments
    openupgrade.logged_query(
        cr,
        "UPDATE ir_attachment SET res_model='contract.contract'"
        + "WHERE res_model='account.analytic.account' "
        + "AND res_id IN ( SELECT DISTINCT "
        + contract_field_name
        + " FROM account_analytic_invoice_line)",
    )
    # Move contract messages
    openupgrade.logged_query(
        cr,
        "UPDATE mail_message SET model='contract.contract'"
        + "WHERE model='account.analytic.account' "
        + "AND res_id IN ( SELECT DISTINCT "
        + contract_field_name
        + " FROM account_analytic_invoice_line)",
    )
    # Move contract followers
    openupgrade.logged_query(
        cr,
        "UPDATE mail_followers SET res_model='contract.contract'"
        + "WHERE res_model='account.analytic.account' "
        + "AND res_id IN ( SELECT DISTINCT "
        + contract_field_name
        + " FROM account_analytic_invoice_line)",
    )


def _copy_contract_line_table(cr):
    contract_line_fields = []
    contract_field_name = _get_contract_field_name(cr)
    for field in CONTRACT_LINE_FIELDS:
        if openupgrade.column_exists(
            cr, 'account_analytic_invoice_line', field
        ):
            contract_line_fields.append(field)
    account_analytic_invoice_line_fields = contract_line_fields.copy()
    contract_line_fields.append('contract_id')
    account_analytic_invoice_line_fields.append(contract_field_name)
    contract_line_fields.append('analytic_account_id')
    account_analytic_invoice_line_fields.append(contract_field_name)
    contract_line_fields.append('active')
    account_analytic_invoice_line_fields.append('true')

    openupgrade.logged_query(
        cr,
        "INSERT INTO contract_line ("
        + ', '.join(contract_line_fields)
        + ") "
        + "SELECT "
        + ', '.join(account_analytic_invoice_line_fields)
        + " FROM account_analytic_invoice_line ",
    )

    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice_line
        SET contract_line_id = contract_line_id_tmp
        """,
    )


def _update_no_update_ir_cron(env):
    # Update ir.cron
    env.ref('contract.contract_cron_for_invoice').model_id = env.ref(
        'contract.model_contract_contract'
    )
    env.ref('contract.contract_line_cron_for_renew').model_id = env.ref(
        'contract.model_contract_line'
    )
    env.ref('contract.email_contract_template').model_id = env.ref(
        'contract.model_contract_contract'
    )


def _init_last_date_invoiced_on_contract_lines(env):
    _logger.info("init last_date_invoiced field for contract lines")
    contract_lines = env["contract.line"].search(
        [("recurring_next_date", "!=", False)]
    )
    contract_lines._init_last_date_invoiced()


def _init_invoicing_partner_id_on_contracts(env):
    _logger.info("Populate invoicing partner field on contracts")
    contracts = env["contract.contract"].search([])
    contracts._inverse_partner_id()


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    _copy_contract_table(cr)
    _copy_contract_line_table(cr)
    _update_no_update_ir_cron(env)

    if parse_version(version) < parse_version('12.0.2.0.0'):
        # We check the version here as this post-migration script was in
        # 12.0.2.0.0 and already done for those who used the module when
        # it was a PR
        _init_last_date_invoiced_on_contract_lines(env)
        _init_invoicing_partner_id_on_contracts(env)
