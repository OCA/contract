This module extends *Contract Invoice Auto Validate*. When a contract invoice
is automatically validated, it is also sent to the customer using their
preferred method (email or Peppol), as configured on the partner.

Sending is per company and only happens when both auto-validation and
auto-sending are enabled. The invoices are queued to the standard asynchronous
"Send Invoices automatically" cron, so the recurring invoices cron is never
blocked by the sending itself.
