This module allows stopping a contract line even after it has been invoiced.

When the stop date is earlier than the last invoiced date, the system will:

- Automatically create a refund invoice for the period between the stop date and the last invoiced date.
- Adjust the `last_date_invoiced` of the contract line to match the stop date.
- Proceed with the normal stop process.

To accurately compute the refund amount, the module depends on
**`contract_variable_qty_prorated`**, which provides the prorating logic used to
determine how much of the previously invoiced quantity should be refunded based
on the actual number of days covered by the refund period.

Without this dependency, it would not be possible to proportionally calculate
the part of the invoiced quantity corresponding to unused service time when a
contract is stopped mid-period.

This ensures that users can gracefully handle early contract terminations
without manual refund management, while maintaining accurate prorated invoicing
and accounting consistency.