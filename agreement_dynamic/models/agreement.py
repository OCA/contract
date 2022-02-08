from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = "agreement"

    model_id = fields.Many2one("ir.model")
    # Inform the user about configured model_id
    # in template
    model_name = fields.Char(related="model_id.name")
    res_id = fields.Integer()
    resource_ref = fields.Reference(
        string="Target record",
        selection="_selection_target_model",
        compute="_compute_resource_ref",
        inverse="_inverse_resource_ref",
    )
    wrapper_report_id = fields.Many2one("ir.ui.view", domain="[('type', '=', 'qweb')]")
    template_id = fields.Many2one(
        "agreement",
        domain="[('is_template', '=', True)]",
        copy=False,
        default=lambda self: self.env.company.external_report_layout_id,
    )
    agreement_ids = fields.One2many(
        "agreement", "template_id", domain="[('is_template', '=', False)]", copy=False
    )
    documentation = fields.Text(default="Some documentation blah blah", readonly=True)
    signature_date = fields.Date(string="Lock Date", copy=False)
    condition_domain_global = fields.Char(
        string="Global domain condition", default="[]"
    )
    active = fields.Boolean(default=True)

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.depends("model_id", "res_id")
    def _compute_resource_ref(self):
        for this in self:
            if this.model_id:
                # we need to give a default to id part of resource_ref
                # otherwise it is not editable
                this.resource_ref = "{},{}".format(
                    this.model_id.model,
                    this.res_id or self.env[this.model_id.model].search([], limit=1).id,
                )
            else:
                this.resource_ref = False

    def _inverse_resource_ref(self):
        for this in self:
            if this.resource_ref:
                this.res_id = this.resource_ref.id
                this.model_id = (
                    self.env["ir.model"]
                    .search([("model", "=", this.resource_ref._name)], limit=1)
                    .id
                )

    def get_template_xml_id(self):
        self.ensure_one()
        if not self.wrapper_report_id:
            # return a default
            return "web.external_layout"
        record = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", self.wrapper_report_id.id)],
            limit=1,
        )
        return "{}.{}".format(record.module, record.name)

    section_ids = fields.One2many("agreement.section", "agreement_id", copy=True)
    section_count = fields.Integer(string="Sections", compute="_compute_section_count")

    @api.depends("section_ids")
    def _compute_section_count(self):
        for this in self:
            this.section_count = len(this.section_ids)

    def action_view_section(self):
        self.ensure_one()
        return {
            "name": _("Sections"),
            "type": "ir.actions.act_window",
            "res_model": "agreement.section",
            "view_mode": "tree,form",
            "target": "current",
            "context": {
                "default_agreement_id": self.id,
                "is_locked": bool(self.signature_date),
            },
            "domain": [("id", "in", self.section_ids.ids)],
        }

    def action_wizard_sign_agreement(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "wizard.sign.agreement",
            "view_mode": "form",
            "target": "new",
        }

    def action_preview_content(self):
        self.ensure_one()
        self._validate_content()
        action = self.env.ref(
            "agreement_dynamic.agreement_dynamic_document_preview"
        ).read([])[0]
        return action

    def action_toggle_active(self):
        self.ensure_one()
        self.active = not self.active

    # Override create() and write() to keep
    # resource_ref always the same with template
    # even if template.resource_ref=False
    @api.model
    def create(self, values):
        records = super().create(values)
        for this in records:
            if this.template_id.resource_ref:
                this.resource_ref = this.template_id.resource_ref
                # Give a default to wrapper_report_id when
                # user sets template_id
                this.wrapper_report_id = this._set_wrapper_report_id(this.template_id)
        return records

    def write(self, values):
        # If the template is changed back to a non-template
        # (eg is_template is set to False),
        # and the template already has children, then disallow.
        if all(
            [
                self.agreement_ids,
                self.is_template,
                "is_template" in values,
                values.get("is_template") is False,
            ]
        ):
            raise UserError(
                _(
                    "You cannot switch this template because "
                    "it has agreements connected to it"
                )
            )
        # If the model is changed while
        # the template already has children, disallow;
        if all(
            [
                self.agreement_ids,
                "model_id" in values,
                self.model_id != self.env["ir.model"].browse(values.get("model_id")),
            ]
        ):
            raise UserError(_("You cannot change model for this agreement"))
        if "template_id" in values and values.get("template_id"):
            # if in an agreement we set a template
            template = self.browse(values.get("template_id"))
            self.resource_ref = template.resource_ref
            # Give a default to wrapper_report_id when
            # user sets template_id
            self.wrapper_report_id = self._set_wrapper_report_id(template)
        return super().write(values)

    def _set_wrapper_report_id(self, template):
        self.ensure_one()
        return template.wrapper_report_id or self.env.company.external_report_layout_id

    def _validate_content(self):
        self.ensure_one()
        # Force user to validate
        # before previewing
        for this in self.section_ids:
            if not this.show_in_report:
                continue
            try:
                this.dynamic_content
            except Exception as e:
                raise UserError(
                    _(
                        "Failed to compute dynamic content"
                        " for section {}. Reason: {}"
                    ).format(this.name or this.id, str(e))
                )
