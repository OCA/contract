The configured behaviour applies automatically to the *Generate Recurring
Invoices from Contracts* cron and to any code relying on
`_get_contracts_to_invoice_domain`:

- *Create recurring invoices* unset: no contract of the company is invoiced.
- *Create recurring invoices* set, no domain: standard behaviour, nothing is
  added.
- *Create recurring invoices* set, with a domain: the domain is applied (with
  AND) to the contracts of the company only.
