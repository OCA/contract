#. Go to Invoicing > Configuration > Contracts > Formulas (quantity).
#. Define any formula based on Python code that stores at some moment a
   float/integer value of the quantity to invoice in the variable 'result'.

   You can use these variables to compute your formula:

   * *env*: Environment variable for getting other models.
   * *context*: Current context dictionary.
   * *user*: Current user.
   * *line*: Contract recurring invoice line that triggers this formula.
   * *contract*: Contract whose line belongs to.
   * *invoice*: Invoice (header) being created.

.. figure:: images/formula_form.png
   :alt: Formula form
   :width: 600 px
