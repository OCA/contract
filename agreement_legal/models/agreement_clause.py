# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AgreementClause(models.Model):
    _name = "agreement.clause"
    _description = "Agreement Clauses"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    title = fields.Char(
        string="Title", help="The title is displayed on the PDF. The name is not."
    )
    sequence = fields.Integer(string="Sequence")
    agreement_id = fields.Many2one("agreement", string="Agreement", ondelete="cascade")
    temp_agreement_id = fields.Many2one(
        "agreement", string="Temp Agreement", help="This field help to filter section."
    )
    section_id = fields.Many2one(
        "agreement.section", string="Section", ondelete="cascade"
    )
    content = fields.Html(string="Clause Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content",
        string="Dynamic Content",
        help="compute dynamic Content",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the agreement without "
        "removing it.",
    )

    # Dynamic field editor
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        help="""Select target field from the related document model. If it is a
         relationship field you will be able to select a target field at the
         destination of the relationship.""",
    )
    sub_object_id = fields.Many2one(
        "ir.model",
        string="Sub-model",
        help="""When a relationship field is selected as first field, this
         field shows the document model the relationship goes to.""",
    )
    sub_model_object_field_id = fields.Many2one(
        "ir.model.fields",
        string="Sub-field",
        help="""When a relationship field is selected as first field, this
         field lets you select the target field within the destination document
          model (sub-model).""",
    )
    default_value = fields.Char(
        string="Default Value",
        help="Optional value to use if the target field is empty.",
    )
    copyvalue = fields.Char(
        string="Placeholder Expression",
        help="""Final placeholder expression, to be copy-pasted in the desired
         template field.""",
    )

    @api.onchange("field_id", "sub_model_object_field_id", "default_value")
    def onchange_copyvalue(self):
        self.sub_object_id = False
        self.copyvalue = False
        if self.field_id and not self.field_id.relation:
            self.copyvalue = "${{object.{} or {}}}".format(
                self.field_id.name,
                self.default_value or "''",
            )
            self.sub_model_object_field_id = False
        if self.field_id and self.field_id.relation:
            self.sub_object_id = self.env["ir.model"].search(
                [("model", "=", self.field_id.relation)]
            )[0]
        if self.sub_model_object_field_id:
            self.copyvalue = "${{object.{}.{} or {}}}".format(
                self.field_id.name,
                self.sub_model_object_field_id.name,
                self.default_value or "''",
            )

    # compute the dynamic content for jinja expression
    def _compute_dynamic_content(self):
        MailTemplates = self.env["mail.template"]
        for clause in self:
            lang = (
                clause.agreement_id and clause.agreement_id.partner_id.lang or "en_US"
            )
            content = MailTemplates.with_context(lang=lang)._render_template(
                clause.content, "agreement.clause", [clause.id]
            )[clause.id]
            clause.dynamic_content = content
