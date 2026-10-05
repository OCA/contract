BUSINESS NEED:
- Your company sells contracts which start dates are not known at the conclusion of the sale.
- Lines which start dates are not confirmed should not be invoiced

APPROACH:
- This module is a bridge between contract_line_defer and product_contract
- It extends the 'defer'-functionality to the sale order line

USEFUL INFORMATION:
- Use the bridge module **contract_line_defer_successor** when also using the module **contract_line_successor**
