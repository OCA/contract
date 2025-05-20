# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def migrate(cr, version):
    cr.execute("UPDATE res_company SET auto_post_contract_invoice=True")
