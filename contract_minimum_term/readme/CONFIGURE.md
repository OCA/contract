- Open a contract template and set the minimum term, the renewal term and the
  termination notice in the **Minimum Term** tab of the template, or of the
  template lines.
- Assign the group `Contract: Terminate Before Minimum Term` to the users
  allowed to terminate contracts before the end of the minimum term. It
  implies the group `Contract: Can Terminate Contracts`.
- The scheduled action **Contract: Renew minimum terms** extends every day the
  minimum terms whose termination notice deadline is over.
