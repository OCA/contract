Contract Invoice Align Start billing cycle
========================================

This module extends the **Contract** module to verify alignment of the start date to the beginning of the configured period.
It creates a specific first period (dummy period) to align the next periods to the first day of the recurring interval.
For example, for a monthly recurrence starting on January 15th, the first invoice will be for January 15th-31st, 
and subsequent invoices will cover the full month (February 1st-28th, etc.).
Proration is automatically applied to the first partial period.
