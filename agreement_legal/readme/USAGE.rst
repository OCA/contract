To use this module:

* Go to Agreement > Agreements
* Create a new agreement
* Select a template
* Follow the process to get the required approval
* Send the invitation to the customer to review and sign the agreement

* Define Field using widget domain but having partial_use option true:
* For Ex:
* <field name="field_domain" widget="domain" nolabel="1"
*                                options="{'model': 'agreement.recital',
*                                'partial_use': True}"/>
