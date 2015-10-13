# -*- coding: utf-8 -*-
from . import models


def copy_recurring_invoice(cr, registry):
    """Copy recurring invoice on contract."""
    cr.execute("UPDATE account_invoice "
               "SET contract_id=aaa.id "
               "FROM account_analytic_account aaa "
               "WHERE aaa.code = account_invoice.origin")
