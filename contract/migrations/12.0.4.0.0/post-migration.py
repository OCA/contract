# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO contract_contract (
            id,
            name,
            partner_id,
            pricelist_id,
            contract_type,
            journal_id,
            company_id,
            analytic_account_id,
            active,
            code,
            group_id,
            contract_template_id,
            user_id,
            recurring_next_date,
            date_end,
            payment_term_id,
            fiscal_position_id,
            invoice_partner_id,
            message_main_attachment_id,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT id,
               name,
               partner_id,
               pricelist_id,
               contract_type,
               journal_id,
               company_id,
               id,
               active,
               code,
               group_id,
               contract_template_id,
               user_id,
               recurring_next_date,
               date_end,
               payment_term_id,
               fiscal_position_id,
               invoice_partner_id,
               message_main_attachment_id,
               create_uid,
               create_date,
               write_uid,
               write_date
        FROM account_analytic_account
        WHERE id in (
            SELECT DISTINCT contract_id FROM account_analytic_invoice_line
        )
        """
    )
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO contract_line (
            id,
            product_id,
            name,
            quantity,
            uom_id,
            automatic_price,
            specific_price,
            discount,
            recurring_rule_type,
            recurring_invoicing_type,
            recurring_interval,
            sequence,
            contract_id,
            date_start,
            date_end,
            recurring_next_date,
            last_date_invoiced,
            termination_notice_date,
            successor_contract_line_id,
            predecessor_contract_line_id,
            manual_renew_needed,
            active,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT id,
               product_id,
               name,
               quantity,
               uom_id,
               automatic_price,
               specific_price,
               discount,
               recurring_rule_type,
               recurring_invoicing_type,
               recurring_interval,
               sequence,
               contract_id,
               date_start,
               date_end,
               recurring_next_date,
               last_date_invoiced,
               termination_notice_date,
               successor_contract_line_id,
               predecessor_contract_line_id,
               manual_renew_needed,
               active,
               create_uid,
               create_date,
               write_uid,
               write_date
        FROM account_analytic_invoice_line
        """
    )
    openupgrade.rename_models(cr, [('account.analytic.invoice.line',
                                    'contract.line')])
    openupgrade.logged_query(
        cr,
        """
        DROP TABLE account_analytic_invoice_line
        """
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice_line
        SET contract_line_id = contract_line_id_tmp
        """
    )
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE account_invoice_line
        DROP COLUMN contract_line_id_tmp
        """
    )
