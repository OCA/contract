# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agreement_type_id = fields.Many2one(
        'agreement.type',
        string='Agreement Type',
        required=True,
        copy=True,
        default=lambda s: s.env['agreement.type'].search([], limit=1),
    )
    agreement_id = fields.Many2one(
        domain=[
            ('is_template', '=', False),
            ('is_customer_requirement', '=', False),
        ],
        readonly=True,
    )

    @api.onchange('agreement_type_id')
    def onchange_agreement_type(self):
        self._update_agreement()

    def _prepare_sale_agreement_values(self):
        return {
            'name': self.agreement_type_id.name,
            'partner_id': self.partner_id.id,
            'agreement_type_id': self.agreement_type_id.id,
            'is_template': False,
        }

    def _update_agreement(self):
        if not self.partner_id:
            return
        if not self.agreement_id and self.partner_id:
            self.agreement_id = self.env['agreement'].create(
                self._prepare_sale_agreement_values()
            )
        agreement_template = self.agreement_type_id.default_agreement_id
        agreement_values = {}
        if agreement_template:
            if not agreement_template.is_template:
                _logger.warn(
                    'The default agreement of the agreement type %s '
                    'is not a template agreement',
                    self.agreement_type_id)
            else:
                agreement_values = \
                    agreement_template.template_prepare_agreement_values(
                        self
                    )
        self.agreement_id.write(agreement_values)

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.agreement_id and not rec.agreement_id.code:
            rec.agreement_id.code = rec.name
        return rec

    @api.multi
    def unlink(self):
        agreements = self.mapped('agreement_id')
        res = super().unlink()
        agreements.sudo().unlink()
        return res

    @api.multi
    def _action_confirm(self):
        self.filtered(lambda r: not r.agreement_id)._update_agreement()
        result = super()._action_confirm()
        self._apply_agreement()
        return result

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'agreement_id' not in default and self.agreement_id:
            new_agreement = self.agreement_id.copy()
            default['agreement_id'] = new_agreement.id
        return super().copy_data(default=default)

    def _apply_agreement(self):
        # Nothing to do for now on the SO itself
        return

    @api.multi
    def _prepare_invoice(self):
        values = super()._prepare_invoice()
        values['agreement_id'] = self.agreement_id.id
        return values


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id=False):
        agreement = self.order_id.agreement_id
        values = super()._prepare_procurement_values(group_id=group_id)
        values['agreement_id'] = agreement.id
        # if agreement.delivery_date:
        #     values['date_planned'] = agreement.delivery_date - timedelta(
        #         days=self.order_id.company_id.security_lead
        #     )
        return values
