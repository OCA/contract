A contract only generates invoices while it is **Active**. *Set to Draft*
holds one that is not agreed yet, and *Cancel* marks one that will never run.
In either of those states the invoicing button is hidden, the recurring cron
passes the contract over, and a direct call to `recurring_create_invoice()`
raises.

New contracts are created **Active**, and so are the contracts that already
existed when the module was installed. Installing this never stops invoicing
that was already happening, and never changes what another module in the
repository does with a contract it just created.

A module that wants contracts to start unapproved changes the default itself.
`contract_tier_validation` does exactly that: there a contract starts in
**Draft** and only reaches **Active** once its reviews have passed.

In the contract list a draft contract is shown in the info colour and a
cancelled one is muted, the way a sale order reads. That sits on top of the
colouring the base view already does by term, so a contract that has expired
or has not started yet still shows as such.

## Extending

The states are a plain selection, so another module can add its own with
`selection_add`, for instance a *Sent* state between draft and active for
contracts that go out to the customer to be signed.

Two hooks keep that additive rather than invasive:

- `_get_invoiceable_states()` returns the states in which a contract may
  invoice. Override it if a state you add should also invoice. Both the
  button visibility and the cron domain read it, so there is one place to
  change.
- The portal record rule excludes draft rather than allowing active, so any
  state you add is visible to the customer without touching security.

This field is the *document workflow* state, in the sense `sale.order.state`
is. It is deliberately not an aggregation of the contract line lifecycle
(`upcoming`, `to-renew`, `closed`), which is a different question and belongs
in a field of its own.

## On the portal

Draft contracts are not visible on the portal at all: a contract still being
prepared internally is nobody's business but yours.

A cancelled one stays visible, and shows the customer a banner saying it has
been cancelled, the way a cancelled quotation does on the sale portal. That
is deliberate. A contract the customer has seen should not silently vanish
from their list, leaving them to wonder whether they misremembered it; they
should be able to open it and read why nothing is happening.
