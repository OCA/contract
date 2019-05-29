# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AgreementAppendix(models.Model):
    _name = "agreement.appendix"
    _description = "Agreement Appendices"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    title = fields.Char(
        string="Title",
        required=True,
        help="The title is displayed on the PDF." "The name is not.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10)
    content = fields.Html(string="Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content",
        string="Dynamic Content",
        help="compute dynamic Content",
    )
    agreement_id = fields.Many2one(
        "agreement",
        string="Agreement",
        ondelete="cascade")
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide this appendix without "
        "removing it.",
    )

    # Dynamic field editor
    field_domain = fields.Char(string='Field Expression',
                               default='[["active", "=", True]]')
    default_value = fields.Char(
        string="Default Value",
        help="Optional value to use if the target field is empty.")
    copyvalue = fields.Char(
        string="Placeholder Expression",
        help="""Final placeholder expression, to be copy-pasted in the desired
         template field.""")

    @api.onchange("field_domain", "default_value")
    def onchange_copyvalue(self):
        self.copyvalue = False
        if self.field_domain:
            string_list = self.field_domain.split(",")
            if string_list:
                field_domain = string_list[0][3:-1]
                self.copyvalue = "${{object.{} or {}}}".format(
                    field_domain,
                    self.default_value or "''")

    # compute the dynamic content for mako expression
    @api.multi
    def _compute_dynamic_content(self):
        MailTemplates = self.env["mail.template"]
        for appendix in self:
            lang = (
                appendix.agreement_id
                and appendix.agreement_id.partner_id.lang
                or "en_US"
            )
            content = MailTemplates.with_context(lang=lang)._render_template(
                appendix.content, "agreement.appendix", appendix.id
            )
            appendix.dynamic_content = content
