To use this module, you need to:

#. Install the contract module
#. Use the markers #START# or #END#.
#. With this module installed
   it is possible to configure the date format using the LDML
   format. See http://babel.pocoo.org/en/latest/dates.html#date-fields

Only date fields are supported.

Examples for 1 September 2018

- #START(MMMM yyyy)# -- September 2018
- #START(d MMMM yy)# -- 1 September 18
- #END(dd MMMM yyy)# -- 01 September 2018
- #END(EEEE dd MMMM yyy)# -- Sunday 01 September 2018
- #START(dd/MM/yyyy) -- 30/09/2018
- #END# -- Default behaviour - Date format on based on partner language
