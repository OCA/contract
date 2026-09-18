This module links `product_contract` and `contract_minimum_term`.

On a contract product, the contract duration can be defined in one of two
exclusive ways:

- **Fixed Duration** (standard behavior of `product_contract`): the contract
  line ends after the duration (e.g. 12 months) and can be renewed
  automatically.
- **Minimum Term**: the contract line is open-ended. It cannot be terminated
  before the end of the minimum term (e.g. 24 months), which is extended by the
  renewal term (e.g. 12 months) if the contract is not terminated in time,
  respecting the termination notice (e.g. 3 months).

A contract line with a minimum term has no end date and cannot be renewed
automatically. The choice and the values are taken over by the sale order lines
and the contract configurator, and passed to the contract lines created from
the sale order.
