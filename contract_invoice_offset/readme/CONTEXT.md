In the standard behavior of the Contract module, invoicing offsets are restricted
to a fixed number of days. While this works for many cases, it is difficult to
configure reliable "in advance" invoicing for intervals like months, given the
varying number of days in each month.

In some business scenarios, a contract must be invoiced exactly one month
in advance (e.g., invoicing January service in December) or with a specific
delay in weeks or years.

This module introduces flexible invoicing offsets, allowing users to define
offsets in Days, Weeks, Months, or Years, ensuring the invoice date is
logically consistent with the billing period regardless of calendar variations.
