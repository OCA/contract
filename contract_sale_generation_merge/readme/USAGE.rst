To use this module, you need to:

1. Go to **Sales -> Orders -> Contracts** and select or create a new contract.
2. Add contract lines with the desired product and quantity.
3. Set the **Generation Type** field to **Sale**
4. Check the **Merge Existing Orders** field. This will merge the contract lines into an existing sale order within the same commitment (delivery) date as the **Date of Next Invoice** field on the contract. If no matching sale order is found, a new one will be created.

To force the sale order generation, enable the **Debug Mode** and click on the **CREATE SALES** button.
