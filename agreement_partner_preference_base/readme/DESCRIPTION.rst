This module builds on the agreement_sale_condition_base module. It allows setting a
preferred agreement type on a customer, and some preferences on the
partner. These preferences are defined in a special type of agreement. The
intent is that additional modules can add fields on an agreement which are m2o
on agreement parameter values. The values of customer preferences are meant to
be used in combination of the value of the template agreement of the agreement
type when the sale order is confirmed.
