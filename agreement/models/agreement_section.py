# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AgreementSection(models.Model):
    _name = 'agreement.section'
    _description = 'Agreement Sections'
    _order = 'sequence'

    name = fields.Char(string="Name", required=True)
    title = fields.Char(string="Title",
                        help="The title is displayed on the PDF."
                             "The name is not.")
    sequence = fields.Integer(string="Sequence")
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
    content = fields.Html(string="Section Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content",
        string="Dynamic Content",
        help='compute dynamic Content')
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the agreement without "
             "removing it."
    )

    # compute the dynamic content for mako expression
    @api.multi
    def _compute_dynamic_content(self):
        MailTemplates = self.env['mail.template']
        for section in self:
            lang = section.agreement_id and \
                section.agreement_id.partner_id.lang or 'en_US'
            content = MailTemplates.with_context(
                lang=lang).render_template(
                section.content, 'agreement.section', section.id)
            section.dynamic_content = content
