This module adds a minimum term handling to contracts, as an alternative to
contract lines with a fixed end date that are renewed automatically.

The contract stays open-ended, but it cannot be terminated before the end of
its minimum term:

- **Minimum term**: when the contract (line) starts, the end of the minimum
  term is computed from the start date (e.g. 24 months). This is the only
  setting the module adds.
- **Renewal**: `is_auto_renew` with `auto_renew_interval` /
  `auto_renew_rule_type` of `contract_line_successor` renews the **minimum
  term** on a line that has one (e.g. 12 more months), instead of an end date.
  Without auto renewal, the contract can be terminated at any time once the
  minimum term is over.
- **Termination notice**: `termination_notice_interval` /
  `termination_notice_rule_type`, also from `contract_line_successor`. The
  termination has to be received at least this long before the end of the
  minimum term, otherwise the minimum term is renewed.

The termination wizard (from `contract_termination`) asks for the date on
which the termination was received, proposes the earliest possible termination
date and refuses an earlier one. Only users of the group
`Contract: Terminate Before Minimum Term` can terminate a contract before
this date, which is logged in the chatter of the contract.

The same rule applies to a single contract line: it cannot be stopped before
that date either, and a line under a minimum term that already started can no
longer be cancelled -- it is stopped, not taken back. A user of the group may
still cancel a line that was never invoiced, to correct a mistake.

A line with a minimum term is open-ended, so it cannot have an end date that is
renewed automatically: both mechanisms would fight over the same line.

Like the recurrence, the minimum term is defined on the contract, or on each
contract line when the recurrence is managed at line level, and taken from the
contract template. The renewal and the notice are set on the lines, where
`contract_line_successor` defines them.
