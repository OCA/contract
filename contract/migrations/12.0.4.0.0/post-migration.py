# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade
from odoo.tools import parse_version

_logger = logging.getLogger(__name__)


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
    contracts = env["contract.contract"].with_context(active_test=False).search([])
    contracts._inverse_partner_id()


def assign_salesman(env):
    """As v11 takes salesman from linked partner and now the salesman is a
    field in the contract that is initialized to current user, we need
    to assign to the recently converted contracts following old logic, or they
    will have admin as responsible.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE contract_contract cc
        SET user_id = rp.user_id
        FROM res_partner rp
        WHERE rp.id = cc.partner_id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_no_update_ir_cron(env)
    if parse_version(version) < parse_version('12.0.2.0.0'):
        # We check the version here as this post-migration script was in
        # 12.0.2.0.0 and already done for those who used the module when
        # it was a PR
        _init_last_date_invoiced_on_contract_lines(env)
        _init_invoicing_partner_id_on_contracts(env)
    assign_salesman(env)
