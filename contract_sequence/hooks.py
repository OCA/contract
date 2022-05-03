# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """
    Updates existing codes matching the default '/' or
    empty. Primarily this ensures installation does not
    fail for demo data.
    :param cr: database cursor
    :return: void
    """
    cr.execute(
        "UPDATE contract_contract "
        "SET name = '!!mig!!' || id "
        "WHERE name IS NULL OR name = '/';"
    )
