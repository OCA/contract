# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    fields_list = [
        ("date", "contract.contract", "contract_contract", "date", "date", "contract")
    ]
    openupgrade.add_fields(env, fields_list)
    query = """
        UPDATE contract_contract
            SET date = date_start
            WHERE date IS NULL
    """
    openupgrade.logged_query(env.cr, query)
