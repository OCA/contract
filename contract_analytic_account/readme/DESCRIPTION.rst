This module adds the *Analytic* (``analytic_distribution``) field on the
contract header (``contract.contract``), using the same analytic
distribution widget already available on contract lines - supporting
several analytic plans at once, not just a single analytic account.

When this field is set or changed, its value is propagated to the
analytic distribution of every contract line. New contract lines created
afterwards also inherit this default automatically, unless they are
created with their own explicit analytic distribution.

A typical use case is linking a contract to the analytic account of a
project (``project.project.analytic_account_id``), the same way purchase
orders are already related to a project through analytic distribution.

It also adds a *Contracts* smart button on the project form, showing the
contracts whose lines are distributed to the project's analytic account.
