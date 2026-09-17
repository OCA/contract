1. **Select a contract** and enable the option **"Recurrence at line level?"**.
2. Once enabled, you will have access to several actions at the contract line level:
   - **Stop** a contract line and optionally **plan a successor**.
   - **Handle temporary suspensions** and **resume** the contract line after the suspension period.
   - **Cancel** and **un-cancel** contract lines if necessary.
   - **Renew** contract lines either by **extending** the current line or by **creating a new successor line** automatically.

The contract lines list is colour-coded by their lifecycle **state** so the
status is readable at a glance (mirroring the contract list and Odoo's own
draft/expired conventions):

- **Upcoming** — blue (like a draft order), the line has not started yet.
- **In-progress** — normal, the line is currently running.
- **To renew** / **Upcoming close** — purple, the line needs attention before
  its end date (distinct from orange/warning, which is kept for real problems).
- **Closed** / **Canceled** — muted/grey, the line is no longer active.
