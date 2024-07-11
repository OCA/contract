Timesheets have a `timesheet_invoice_type` field which tells if they are
billable or not, and if billable of which type.  In the `sale_timesheet` module,
this field gets a billable type only when the timesheet are linked to a sale
order line.

When billing with recurring invoices using the OCA `contract` module, we often
work without sale order. So this module is useful to allow correctly
categorizing as billable timesheets on projects that are billed using recurring
contracts.
