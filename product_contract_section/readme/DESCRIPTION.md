- Base `product_contract` only copies the order lines whose product is a
  contract product, so section and note lines are lost when a contract is
  generated from a sale order.
- This module propagates the sale order's section and note lines to the
  generated contract:

  - each display line is attached to the contract(s) of the product lines
    placed beneath it,
  - a section shared by several contracts is repeated in each of them,
  - the original ordering is preserved.
