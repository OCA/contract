To configure this module:

1. Go to *Settings > Contracts*.
2. Enable *Auto validate contract invoices* for the company.
3. The *Auto send contract invoice* option then appears below it; enable it to
   send the validated invoices to customers.
4. Optionally set the *Auto-Send Invoice Author*, the partner recorded as the
   author of the sent invoices. It defaults to the company's own partner.

The setting is per company, so switch the active company to configure another
one. The sending method (email or Peppol) is taken from each customer's
configuration.

Sending is handled by the standard *Send invoices automatically* scheduled
action (`account.ir_cron_account_move_send`). If that cron is deactivated, the
invoices are validated but not queued for sending, and a warning is logged.
