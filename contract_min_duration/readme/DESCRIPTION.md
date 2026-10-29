This module extends the **Contract** module to enforce a minimum contract duration.

It adds a `min_contract_end_date` field to contracts. If a user attempts to set an end date (e.g., via termination) that is earlier than this minimum date, the system automatically extends the end date to the minimum required date, ensuring the customer is invoiced for the full minimum period.
