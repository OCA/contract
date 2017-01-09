# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copys = {
    'account_analytic_account': [
        (openupgrade.get_legacy_name('date_start'), 'date_start', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copys)
    openupgrade.update_module_names(
        cr, [
            ('hr_timesheet_invoice', 'contract'),
            ('contract_journal', 'contract'),
            ('contract_discount', 'contract'),
            ('contract_recurring_invoicing_marker', 'contract'),
            ('contract_recurring_invoicing_monthly_last_day', 'contract'),
            ('contract_show_recurring_invoice', 'contract'),
        ], merge_modules=True,
    )
