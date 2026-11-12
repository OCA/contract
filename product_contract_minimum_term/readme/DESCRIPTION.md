This module links `product_contract` and `contract_minimum_term`.

On a contract product, the contract duration can be defined in one of two
exclusive ways:

- **Fixed Duration** (standard behavior of `product_contract`): the contract
  line ends after the duration (e.g. 12 months). With **Auto Renew**, the line
  gets a new end date at each renewal.
- **Minimum Term**: the contract line is open-ended. It cannot be terminated
  before the end of the minimum term (e.g. 24 months). With **Auto Renew**,
  the minimum term itself is renewed (e.g. 12 more months) when the contract
  is not terminated within the termination notice.

The renewal and the termination notice are the fields `product_contract`
already has, so the only new settings are the minimum term and the choice
between the two durations. Both are taken over by the sale order lines and the
contract configurator, and passed to the contract lines created from the sale
order. A line with a minimum term is created without end date.
