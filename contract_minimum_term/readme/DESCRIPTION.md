This module adds a minimum term handling to contracts, as an alternative to
contract lines with a fixed end date that are renewed automatically.

The contract stays open-ended, but it cannot be terminated before the end of
its minimum term:

- **Minimum term**: when the contract (line) starts, the end of the minimum
  term is computed from the start date (e.g. 24 months).
- **Renewal term**: if the contract is not terminated in time, the minimum term
  is extended by the renewal term (e.g. 12 months). Without a renewal term, the
  contract can be terminated at any time once the minimum term is over.
- **Termination notice**: the termination has to be received at least this
  long before the end of the minimum term (e.g. 3 months), otherwise the
  minimum term is renewed. Once the minimum term is over (without renewal
  term), the termination date has to respect the termination notice.

The termination wizard (from `contract_termination`) asks for the date on
which the termination was received, proposes the earliest possible termination
date and refuses an earlier one. Only users of the group
`Contract: Terminate Before Minimum Term` can terminate a contract before
this date, which is logged in the chatter of the contract.

Like the recurrence, the minimum term is defined on the contract, or on each
contract line when the recurrence is managed at line level. The values are
taken from the contract template.
