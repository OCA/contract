This module adds spreadsheet dashboards for subscriptions, built on top of the
community ``spreadsheet_dashboard`` engine and the analysis models provided by
``subscription_oca``. No enterprise dependency is required.

It ships four ready-to-use dashboards under the **Dashboards** application, in a
dedicated *Subscriptions* group:

* **Subscriptions**: monthly/annual recurring revenue, active subscriptions and
  average MRR, with breakdowns by template, product category, sales team,
  salesperson, start month and stage.
* **Salesperson**: recurring revenue and number of subscriptions broken down by
  salesperson and sales team.
* **MRR Evolution**: net/new/churned MRR and the cumulated MRR over time, with a
  monthly new-vs-churn breakdown. MRR change events are derived from the current
  state of the subscriptions (a positive event at the start date and a negative
  one at the closing date); mid-life expansion/contraction is not tracked, which
  would require a dedicated MRR event log.
* **Retention**: cohort sizes and recurring revenue per start month, plus a
  retention/survival curve built from the start and closing dates.

All dashboards expose global filters (salesperson, sales team, customer,
template) and refresh automatically from the subscription analysis models.
