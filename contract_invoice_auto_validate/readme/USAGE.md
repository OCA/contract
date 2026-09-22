Before installing this addon make sur that "CONTRACT_INVOICE" queue
channel has at maximum a capacity=1 in the odoo configuration file.
Otherwise you will have concurrency access issue between jobs to the
account.move sequence.

Example:

\[queue_job\] channels=root:5,root.CONTRACT_INVOICE:1
