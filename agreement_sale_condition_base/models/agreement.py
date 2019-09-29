# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    code = fields.Char(required=False)
    sale_ids = fields.One2many(
        'sale.order', 'agreement_id', string="Sale Orders"
    )
    is_sale_agreement = fields.Boolean(
        'Sale Agreement?', compute='_compute_is_sale_agreement', store=True
    )

    @api.depends('sale_ids')
    def _compute_is_sale_agreement(self):
        for rec in self:
            rec.is_sale_agreement = bool(rec.sale_ids)

    @api.model
    def _get_sale_agreement_fields(self):
        """return a list of field names which are related to sale conditions"""
        # extend the list in modules implementing specific conditions
        return []

    def _get_agreement_fields(self):
        return []

    def template_prepare_agreement_values(self, sale_order):
        self.ensure_one()
        assert self.is_template, \
            (
                'Programming error: '
                'this method must only be called on a template agreement'
            )
        fields = ['agreement_type_id'] + self._get_agreement_fields()
        tmpl_values = self.read(fields, load='_classic_write')[0]
        del tmpl_values['id']
        tmpl_values.update(
            {
                'name': self.agreement_type_id.name,
                'is_template': False,
            }
        )
        return tmpl_values

    @api.multi
    def write(self, values):
        res = super().write(values)
        if values.get('agreement_type_id'):
            self._check_agreement_type_default_agreement()
        return res

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        res = super().create(vals_list)
        res._check_agreement_type_default_agreement()
        return res

    def _check_agreement_type_default_agreement(self):
        # if we are setting an agreement type on a template agreement then the
        # template agreement becomes the default agreement of the agreement
        # type
        template_agreements = self.filtered('is_template')
        for template in template_agreements:
            agreement_type = template.agreement_type_id
            if not agreement_type.default_agreement_id:
                agreement_type.default_agreement_id = template
            elif agreement_type.default_agreement_id == template:
                continue
            else:
                raise exceptions.UserError(
                    _('It is forbidden to have 2 templates in the '
                      'same agreement type.')
                )
