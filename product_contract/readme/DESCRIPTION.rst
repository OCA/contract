This module adds support for products to be linked to contract templates.

A contract is created on ``sale.order`` confirmation for each different template used in sale order line where recurrence details are set too.

Contract product are ignored on invoicing process and pass to nothing to invoice directly.
