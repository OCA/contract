- Business need:

  - quotations are often structured with sections and notes to group the
    services offered,
  - when the sale is confirmed and a contract is generated, that structure
    should be kept so the contract and its invoices read like the quotation.

- Approach:

  - hook into the contract generation of `product_contract`,
  - recreate the section and note lines on the generated contract(s).

- Useful information:

  - depends on `product_contract`,
  - works well together with `contract_layout_category_hide_detail`, which
    also propagates the per-section display settings.
