Glue between `contract_state` and `contract_termination`. Terminating a
contract with the termination wizard moves it to a **Terminated** state, so the
state bar, list badge and filters show where every contract is:
Draft, Active, Terminated or Cancelled.

Cancelling the termination puts the contract back to Active. Contracts that
were already terminated get the state when the module is installed.

A terminated contract can still raise its closing invoice; whether the
recurring run still picks it up is left to `contract_termination`.
