The **Contract Termination** module extends the `contract` module, allowing
users to properly manage the termination of contracts.  
It provides functionality to terminate contracts with a reason, track
termination comments and dates, and prevent further modifications on terminated
contracts unless reactivated.

## Features

- **Terminate Contracts**
  - Users with the appropriate rights can terminate active contracts.
  - Capture a termination reason, comment, and termination date.

- **Update or Cancel Termination**
  - Update termination details if needed.
  - Cancel (reactivate) a terminated contract.

- **Contract Form Enhancements**
  - Display an alert on terminated contracts with the reason and comment.
  - Hide or disable contract actions (e.g., Send) and fields on terminated contracts.
  - Set contract fields as read-only after termination.

- **Permissions**
  - Only users with the group `Contract: Can Terminate Contracts` can terminate
    or cancel termination of contracts.
