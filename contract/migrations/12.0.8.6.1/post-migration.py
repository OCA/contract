#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    to_fix_contract_lines = env['contract.line'].search([
        ('state', 'not in', ('closed', 'canceled')),
        ('recurring_next_date', '=', False),
    ])
    to_fix_contract_lines._onchange_date_start()
