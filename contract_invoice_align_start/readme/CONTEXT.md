This module aligns the contract invoicing cycle to the beginning of the period (usually the month).

**Standard Behavior (Without this module):**
If a contract starts on January 15th with a monthly recurrence, the billing periods are:
*   January 15th to February 14th
*   February 15th to March 14th
*   etc.

**Aligned Behavior (With this module):**
If "Align Billing Cycle to First Day of Month" is enabled:
*   **First Period:** January 15th to January 31st (Prorated)
*   **Second Period:** February 1st to February 28th
*   **Subsequent Periods:** Full months starting from the 1st.

This ensures that invoices are generated for standard calendar months, which is often preferred for accounting and subscription management.
