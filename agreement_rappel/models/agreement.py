# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class Agreement(models.Model):
    _inherit = 'agreement'

    def _selection_rappel_type(self):
        return [
            ('global', 'Global (A discount global for all lines)'),
            ('line', 'Line (A discount for every line)'),
            ('section_total', 'Compute total and apply discount rule match'),
            ('section_prorated', 'Compute multi-dicounts by sections amount'),
        ]

    rappel_type = fields.Selection(
        selection=lambda self: self._selection_rappel_type(),
        string='Rappel type',
    )
    rappel_line_ids = fields.One2many(
        comodel_name='agreement.rappel.line',
        string='Agreement rappel lines',
        inverse_name='agreement_id',
        copy=True,
    )
    rappel_section_ids = fields.One2many(
        comodel_name='agreement.rappel.section',
        string='Agreement rappel sections',
        inverse_name='agreement_id',
        copy=True,
    )
    rappel_discount = fields.Float(
        string='Rappel discount',
    )


class AgreementRappelLine(models.Model):
    _name = 'agreement.rappel.line'
    _description = 'Agreement Rappel Lines'

    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
    )
    rappel_target = fields.Selection([
        ('product', 'Product variant'),
        ('product_tmpl', 'Product templates'),
        ('category', 'Product categories'),
        ('condition', 'Rappel condition'),
        ('domain', 'Rappel domain'),
    ])
    rappel_product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Products',
    )
    rappel_product_tmpl_ids = fields.Many2many(
        comodel_name='product.template',
        string='Product templates',
    )
    rappel_category_ids = fields.Many2many(
        comodel_name='product.category',
        string='Product categories',
    )
    rappel_condition_id = fields.Many2one(
        comodel_name='agreement.rappel.condition',
        string='Rappel condition',
    )
    rappel_domain = fields.Char(
        compute='_compute_rappel_domain',
        inverse=lambda self: self,
        string='Rappel domain',
        store=True,
    )
    rappel_discount = fields.Float(string='Rappel discount')

    @api.depends(
        'rappel_target', 'rappel_product_ids', 'rappel_product_tmpl_ids',
        'rappel_category_ids', 'rappel_condition_id')
    def _compute_rappel_domain(self):
        for line in self:
            if line.rappel_target == 'product':
                line.rappel_domain = [
                    ('product_id', 'in', line.rappel_product_ids.ids)
                ]
            elif line.rappel_target == 'product_tmpl':
                line.rappel_domain = [
                    ('product_id.product_tmpl_id', 'in',
                     line.rappel_product_tmpl_ids.ids)
                ]
            elif line.rappel_target == 'category':
                line.rappel_domain = [
                    ('product_id.categ_id', 'in',
                     line.rappel_category_ids.ids)
                ]
            elif line.rappel_target == 'condition':
                line.rappel_domain = line.rappel_condition_id.rappel_domain


class AgreementRappelCondition(models.Model):
    _name = 'agreement.rappel.condition'
    _description = 'Agreement Rappel Condition'

    name = fields.Char(string='Rappel condition')
    rappel_domain = fields.Char(string='Domain')


class AgreementRappelSection(models.Model):
    _name = 'agreement.rappel.section'
    _description = 'Agreement Rappel Section'

    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
    )
    amount_from = fields.Float(string="From")
    amount_to = fields.Float(string="To")
    rappel_discount = fields.Float(string="% Dto")
