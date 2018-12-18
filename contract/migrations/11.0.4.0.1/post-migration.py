# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Copy the name to name_on_contract."""
    cr.execute("""UPDATE account_analytic_contract_line
        SET name_on_contract = name""")
