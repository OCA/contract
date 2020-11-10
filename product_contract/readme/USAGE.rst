To use this module, you need to:

#. Go to Sales -> Products and select or create a product.
#. Check "Is a contract" and select the contract template related to the
   product
#. Define default recurrence rules

For contract products, the contract template is set on the product template,
and automatically set on its variants.
It is then possible to modify the contract template independently on each variant.
Afterwards, modifying the variant on the product template modifies it only on variants
for which the default value was not modified.

There is a setting to constrain any contract product to have a contract template.
Note that this is verified at the variant level, so if all variants have a contract
template, it is possible to unset it on their product template.
