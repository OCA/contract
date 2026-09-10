Suspension reasons can be configured from:

    Sales > Configuration > Automatic Invoice Suspension Reason

Each reason can have:

* **Name**: the name of the suspension reason.
* **Sequence**: the order in which reasons are displayed.
* **Parent**: an optional parent reason used to create a hierarchy.
* **Can be selected**: determines whether the reason can be selected when
  suspending automatic invoicing.
* **Company**: the company to which the reason belongs.

A reason can be used as a category by creating child reasons underneath it.
For example:

* Maintenance
    * Scheduled Maintenance
    * Emergency Maintenance

When a child reason is selected, its top-level category is automatically
identified.
