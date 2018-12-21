# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AgreementRecital(models.Model):
    _name = 'agreement.recital'
    _description = 'Agreement Recitals'
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    title = fields.Char(string="Title",
                        help="The title is displayed on the PDF."
                             "The name is not.")
    sequence = fields.Integer(string="Sequence", default=10)
    content = fields.Html(string="Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content",
        string="Dynamic Content",
        help='compute dynamic Content')
    agreement_id = fields.Many2one('agreement', string="Agreement",
                                   ondelete="cascade")
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide this recital without "
             "removing it.")

    # compute the dynamic content for mako expression
    @api.multi
    def _compute_dynamic_content(self):
        MailTemplates = self.env['mail.template']
        for recital in self:
            lang = recital.agreement_id and \
                recital.agreement_id.partner_id.lang or 'en_US'
            content = MailTemplates.with_context(
                lang=lang).render_template(
                recital.content, 'agreement.recital', recital.id)
            recital.dynamic_content = content
