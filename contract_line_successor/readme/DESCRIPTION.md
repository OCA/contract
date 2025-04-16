**Contract Line Successor** extends `contract.line` model to support advanced
contract lifecycle management, including suspension, successor planning,
cancellation, and renewal.  
It provides a flexible and robust framework for managing complex contract
line scenarios in a clean and structured way.

## Features

- **Successor and Predecessor Management**
  - Link contract lines with successor and predecessor lines.
  - Plan successors automatically or manually after a stop or suspension.

- **Contract Line Lifecycle States**
  - Manage contract lines with the following computed states:
    - `Upcoming`
    - `In-Progress`
    - `To Renew`
    - `Upcoming Close`
    - `Closed`
    - `Canceled`

- **Lifecycle Operations**
  - Stop a contract line.
  - Plan a successor for a contract line.
  - Stop and plan a successor in one operation (useful for suspensions).
  - Cancel and un-cancel contract lines.
  - Renew contract lines automatically (new line or extension).

- **Auto-Renewal Handling**
  - Auto-renewal based on company settings (extend existing line or create a new one).
  - Cron job to automate renewal of eligible contract lines.

- **Data Integrity and Validation**
  - Prevent invalid successor or predecessor configurations.
  - Validate state transitions and date overlaps.
  - Ensure clean renewal and cancellation workflows.

- **Audit Trail**
  - Automatic posting of chatter messages for lifecycle events like stops, 
    renewals, suspensions, cancellations, etc.
