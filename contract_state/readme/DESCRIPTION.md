Adds a document workflow state to contracts: **Draft**, **Active** and
**Cancelled**.

A contract only generates invoices while it is active. Draft is for a contract
that is not agreed yet: the invoicing button is hidden, the recurring cron
passes it over, and the customer does not see it in the portal. Cancelled is
for one that will never run, and stays visible to the customer with a banner.

Contracts are created active, so installing this module does not stop any
invoicing. Modules that need a contract to be approved before it runs, such as
`contract_tier_validation`, change that default themselves.
