The contract_forecast module enhances the **Contract** module by
generating and managing **forecast periods** for each contract line. It
automatically calculates future invoicing amounts and dates, allowing
companies to better anticipate and report on expected revenues.

Forecasts are visible directly from the contract in a **pivot view** or
**list view**.

\## Features

- Generate forecast periods based on the contract's invoicing rules.
- View forecasts grouped by invoice date.
- Automatic regeneration of forecast periods when contract data changes
  (product, quantity, price, dates, etc.).
- Company-wide configuration to enable or disable forecasts.
- Configurable forecast interval and period type (monthly or yearly).
- Forecast period data includes:
  - Start and end dates
  - Expected invoice date
  - Quantity, unit price, discount, and subtotal (untaxed)
- Clean handling of auto-renewing and manually-ended contracts.
