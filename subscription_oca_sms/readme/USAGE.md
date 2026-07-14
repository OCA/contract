On a subscription form, salespeople (group *Sales / User*) get two
buttons next to *Close subscription*:

- **SMS payment reminder** — sends the customer an SMS reminding them of
  the next invoice date.
- **SMS payment failure** — notifies the customer that a payment could
  not be processed.

Both are **manual, one-click** actions: the salesperson decides when to
send. The buttons only appear when the customer has a valid phone
number. The SMS body is automatically translated to the customer's
language if a translation of the template exists.

Sending SMS relies on Odoo's SMS gateway (IAP), which has a per-message
cost. Make sure the gateway is configured and has credit before using
these actions.
