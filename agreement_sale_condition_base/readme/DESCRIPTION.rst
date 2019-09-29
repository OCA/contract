This module builds on the agreement and agreement_sale modules. It defines a
model for agreement parameter values. The intent is that additional modules can
add fields on an agreement which are m2o on to parameter values, and possibly
the allowed values for a given field could depend on the value of another one.

An agreement type can be linked to a template agreement. When the agreement
type is set on a sale order, a new agreement record is created using the
template agreement as a basis. This agreement specific to the sale order can be
customized by the sales man.

A preferred agreement type can be set on on a customer, and some preferences on the
partner. These preferences are defined in a special type of agreement. The
intent is that additional modules can add fields on an agreement which are m2o
on agreement parameter values. The values of customer preferences are meant to
be used in combination of the value of the template agreement of the agreement
type when the sale order is confirmed.

When the sale order is confirmed, the agreement of the sale order is propagated
to the procurement group of the sale order. This can be used by extension
modules to customize the generation of the stock moves and pickings to match
the agreement.

In a similar fashion, when an invoice is created from the sale order, the
agreement of the sale order, the agreement is propagated to the invoice.
