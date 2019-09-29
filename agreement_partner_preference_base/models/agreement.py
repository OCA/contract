# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    is_customer_requirement = fields.Boolean('Customer requirement?')

    @api.model
    def _get_customer_agreement_fields(self):
        """return a list of field names which are related to sale conditions"""
        # extend the list in modules implementing specific conditions
        return []

    def _values_for_clear_defaults(self):
        values = {}
        for field in self._get_customer_agreement_fields():
            values[field] = False
        return values

    @api.onchange('is_template')
    def onchange_is_template(self):
        if self.is_template:
            self.unset_customer_defaults()
            self.partner_id = False

    def unset_customer_defaults(self):
        values = self._values_for_clear_defaults()
        for rec in self:
            rec.update(values)

    @api.onchange('is_customer_requirement')
    def onchange_is_customer(self):
        if self.is_customer_requirement:
            self.is_template = False
            self.set_customer_defaults()

    def _get_customer_defaults_values(self):
        ParameterValue = self.env['agreement.parameter.value']
        values = {}
        for field in self._get_customer_agreement_fields():
            values[field] = ParameterValue.get_default(field)
        return values

    def set_customer_defaults(self):
        values = self._get_customer_defaults_values()
        for rec in self:
            rec.update(values)

    def template_prepare_agreement_values(self, sale_order):
        values = super().template_prepare_agreement_values(sale_order)
        values.update({'is_customer_requirement': False})
        partner = sale_order.partner_id
        customer_settings = partner.customer_agreement_settings_id
        assert not customer_settings or \
            customer_settings.is_customer_requirement, \
            'customer_settings must be a customer requirement agreement'
        if customer_settings:
            fields = self._get_customer_agreement_fields()
            cust_vals = customer_settings.read(
                fields, load='_classic_write'
            )[0]
            del cust_vals['id']
            values.update(cust_vals)
            values['name'] = self.agreement_type.name
        return values
