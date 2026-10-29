- Open a contract template and set the minimum term in the **Minimum Term**
  tab, or per template line in the **Renewal** tab, together with the renewal
  (`Auto Renew`) and the termination notice.
- Assign the group `Contract: Terminate Before Minimum Term` to the users
  allowed to terminate contracts before the end of the minimum term. It
  implies the group `Contract: Can Terminate Contracts`.
- The scheduled action **Contract: Renew minimum terms** extends every day the
  minimum terms whose termination notice deadline is over.
