# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


# Main Agreement Section Records Model
class AgreementSection(models.Model):
    _name = 'agreement.section'
    _order = 'section_sequence'

    # General
    name = fields.Char(
        string="Title",
        required=True
    )
    section_sequence = fields.Integer(
        string="Sequence"
    )
    agreement_id = fields.Many2one(
        'agreement',
        string="Agreement",
        ondelete="cascade"
    )
    clauses_ids = fields.One2many(
        'agreement.clause',
        'section_id',
        string="Clauses"
    )
    content = fields.Html(
        string="Section Content"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the agreement without "
             "removing it."
    )

    # Placeholder fields
    model_id = fields.Many2one(
        'ir.model',
        string="Applies to",
        help="The type of document this template can be used with."
    )
    model_object_field_id = fields.Many2one(
        'ir.model.fields',
        string="Field",
        help="Select target field from the related document model. If it is a "
             "relationship field you will be able to select a target field at "
             "the destination of the relationship."
    )
    sub_object_id = fields.Many2one(
        'ir.model',
        string="Sub-model",
        help="When a relationship field is selected as first field, this "
             "field shows the document model the relationship goes to."
    )
    sub_model_object_field_id = fields.Many2one(
        'ir.model.fields',
        string="Sub-field",
        help="When a relationship field is selected as first field, this "
             "field lets you select the target field within the destination "
             "document model (sub-model)."
    )
    null_value = fields.Char(
        string="Default Value",
        help="Optional value to use if the target field is empty."
    )
    copyvalue = fields.Char(
        string="Placeholder Expression",
        help="Final placeholder expression, to be copy-pasted in the desired "
             "template field."
    )

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('agreement.section') or '/'
        vals['section_sequence'] = seq
        return super(AgreementSection, self).create(vals)
