This module extends `Contract` and delegates invoicing contracts to jobs.

When invoicing a large number of contracts, the task is delegated to jobs to avoid server time-outs.

This applies to:
- Auto invoicing (cron)
- Manual invoicing (wizard)
