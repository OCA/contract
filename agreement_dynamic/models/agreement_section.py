import copy

from lxml import etree

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import safe_eval

from .header import Header

try:
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    # Let's keep these in case they are needed
    # in the future
    mako_template_env.globals.update(
        {
            "str": str,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "filter": filter,
            "map": map,
            "round": round,
            "page": "<p style='page-break-after:always;'/>",
        }
    )
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    pass


class AgreementSection(models.Model):
    _name = "agreement.section"
    _description = "Agreement Section"

    _order = "sequence"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Don't allow any cud operations for locked sections
        result = super(AgreementSection, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        view_id_tree = self.env.ref("agreement_dynamic.view_agreement_section_tree").id
        view_id_form = self.env.ref("agreement_dynamic.view_agreement_section_form").id
        if (
            all([view_id_tree == result["view_id"], view_type == "tree"])
            or all([view_id_form == result["view_id"], view_type == "form"])
        ) and self.env.context.get("is_locked"):
            arch = etree.fromstring(result["arch"])
            arch.attrib["create"] = "false"
            arch.attrib["edit"] = "false"
            arch.attrib["delete"] = "false"
            result["arch"] = etree.tostring(arch)
        return result

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence", default=10)
    content = fields.Html("Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content", string="Dynamic Content",
    )
    agreement_id = fields.Many2one("agreement", string="Agreement", ondelete="cascade")
    resource_ref = fields.Reference(related="agreement_id.resource_ref")
    res_id = fields.Integer(related="agreement_id.res_id")
    resource_ref_model_id = fields.Many2one("ir.model", related="agreement_id.model_id")

    # Dynamic field editor
    field_id = fields.Many2one("ir.model.fields", string="Field")
    sub_object_id = fields.Many2one("ir.model", string="Sub-model")
    sub_model_object_field_id = fields.Many2one("ir.model.fields", string="Sub-field")
    default_value = fields.Char("Default Value")
    copyvalue = fields.Char("Placeholder Expression")
    is_paragraph = fields.Boolean(
        default=True, string="Paragraph", help="To highlight lines"
    )
    condition_python = fields.Text(
        string="Python Condition", help="Condition for rendering section",
    )
    condition_domain = fields.Char(string="Domain Condition", default="[]")
    condition_python_preview = fields.Char("Preview", compute="_compute_condition")
    show_in_report = fields.Boolean(compute="_compute_condition")
    model_id_model = fields.Char(
        string="Model _description", related="agreement_id.model_id.model"
    )

    @api.onchange("field_id", "sub_model_object_field_id", "default_value")
    def onchange_copyvalue(self):
        self.sub_object_id = False
        self.copyvalue = False
        if self.field_id and not self.field_id.relation:
            self.copyvalue = "${{object.{} or {}}}".format(
                self.field_id.name, self._get_proper_default_value()
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
                self._get_proper_default_value(),
            )

    @api.onchange("condition_python")
    def _compute_condition(self):
        """Compute condition and preview"""
        for this in self:
            this.condition_python_preview = this.show_in_report = False
            condition_python = (
                this.condition_python.strip() if this.condition_python else ""
            )
            condition_domain = (
                this.condition_domain.strip() if this.condition_domain else "[]"
            )
            if not this.resource_ref_model_id:
                continue
            if not this.res_id:
                continue
            # search for a record for this.res_id and this.model_id
            record = this.resource_ref.filtered_domain(safe_eval(condition_domain))
            if not record:
                continue
            if not condition_python:
                this.show_in_report = True
                continue
            try:
                # Check if there are any syntax errors etc
                this.condition_python_preview = safe_eval(
                    condition_python, {"object": record}
                )
            except Exception as e:
                # and show debug info
                this.condition_python_preview = str(e)
                continue
            is_valid = bool(this.condition_python_preview)
            this.show_in_report = is_valid
            if not is_valid:
                # Preview is there, but condition is false
                this.condition_python_preview = "False"

    def _get_proper_default_value(self):
        self.ensure_one()
        is_num = self.field_id.ttype in ("integer", "float")
        value = 0 if is_num else "''"
        if self.default_value:
            if is_num:
                value = "{}"
            else:
                value = "'{}'"
            value = value.format(self.default_value)
        return value

    # compute the dynamic content for jinja expression
    def _compute_dynamic_content(self):
        # a parent with two children
        h = self._get_header_object()
        for this in self:
            prerendered_content = this._prerender()
            content = this._render_template(
                prerendered_content,
                this.resource_ref_model_id.model,
                this.res_id,
                datas={"h": h},
            )
            this.dynamic_content = content

    def _get_header_object(self):
        h = Header(child=Header(child=Header()))
        return h

    def _prerender(self):
        """Substitute expressions using agreement.dynamic.alias records"""
        self.ensure_one()
        content = self.content
        for alias in self.env["agreement.dynamic.alias"].search(
            [("is_active", "=", True)]
        ):
            if alias.expression_from not in content:
                continue
            content = content.replace(alias.expression_from, alias.expression_to)
        return content

    @api.model
    def _render_template(self, template_txt, model, res_ids, datas=False):
        """
        Render input provided by user, for report and preview
        It is an edited version of mail.template._render_template()
        """
        if isinstance(res_ids, int):
            res_ids = [res_ids]
        if datas and not isinstance(datas, dict):
            raise UserError(_("datas argument is not a proper dict"))
        results = dict.fromkeys(res_ids, u"")
        # try to load the template
        mako_env = mako_safe_template_env
        template = mako_env.from_string(tools.ustr(template_txt))
        records = self.env[model].browse(
            it for it in res_ids if it
        )  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record
        # prepare template variables
        variables = {
            "ctx": self._context,  # context kw would clash with mako internals
        }
        if datas:
            variables.update(datas)
        for res_id, record in res_to_rec.items():
            variables["object"] = record
            try:
                render_result = template.render(variables)
            except Exception as e:
                raise UserError(
                    _("Failed to render template %r using values %r")
                    % (template, variables)
                    + "\n\n{}: {}".format(type(e).__name__, str(e))
                )
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result
        return results[res_ids[0]] or results

    # Don't create/write sections for locked agreements
    @api.model
    def create(self, values):
        records = super().create(values)
        for this in records:
            if this.agreement_id.signature_date:
                raise UserError(_("You cannot create a section for a locked agreement"))
        return records

    def write(self, values):
        for this in self:
            if this.agreement_id.signature_date:
                raise UserError(_("You cannot edit a section for a locked agreement"))
        return super().write(values)
