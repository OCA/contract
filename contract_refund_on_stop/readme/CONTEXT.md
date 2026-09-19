In the standard behavior of the Contract module, it is not possible to stop
a contract line if its stop date is earlier than the last invoiced date.
This restriction prevents users from adjusting contracts that were invoiced
too far in advance.

In some business cases, however, a contract may need to be stopped retroactively
(e.g., customer cancellation, early termination, or service interruption).
In such cases, it is necessary to **automatically create a refund**
for the invoiced period that should no longer be billed.
