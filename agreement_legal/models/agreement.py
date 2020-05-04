# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    # General
    name = fields.Char(string="Title", required=True)
    version = fields.Integer(
        string="Version",
        default=1,
        copy=False,
        help="The versions are used to keep track of document history and "
        "previous versions can be referenced.")
    revision = fields.Integer(
        string="Revision",
        default=0,
        copy=False,
        help="The revision will increase with every save event.")
    description = fields.Text(
        string="Description",
        track_visibility="onchange",
        help="Description of the agreement")
    dynamic_description = fields.Text(
        compute="_compute_dynamic_description",
        string="Dynamic Description",
        help="Compute dynamic description")
    start_date = fields.Date(
        string="Start Date",
        track_visibility="onchange",
        help="When the agreement starts.")
    end_date = fields.Date(
        string="End Date",
        track_visibility="onchange",
        help="When the agreement ends.")
    color = fields.Integer(string="Color")
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the agreement without "
        "removing it.")
    company_signed_date = fields.Date(
        string="Signed on",
        track_visibility="onchange",
        help="Date the contract was signed by Company.")
    partner_signed_date = fields.Date(
        string="Signed on (Partner)",
        track_visibility="onchange",
        help="Date the contract was signed by the Partner.")
    term = fields.Integer(
        string="Term (Months)",
        track_visibility="onchange",
        help="Number of months this agreement/contract is in effect with the "
        "partner.")
    expiration_notice = fields.Integer(
        string="Exp. Notice (Days)",
        track_visibility="onchange",
        help="Number of Days before expiration to be notified.")
    change_notice = fields.Integer(
        string="Change Notice (Days)",
        track_visibility="onchange",
        help="Number of Days to be notified before changes.")
    special_terms = fields.Text(
        string="Special Terms",
        track_visibility="onchange",
        help="Any terms that you have agreed to and want to track on the "
        "agreement/contract.")
    dynamic_special_terms = fields.Text(
        compute="_compute_dynamic_special_terms",
        string="Dynamic Special Terms",
        help="Compute dynamic special terms")
    code = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: _("New"),
        track_visibility="onchange",
        copy=False,
        help="ID used for internal contract tracking.")
    increase_type_id = fields.Many2one(
        "agreement.increasetype",
        string="Increase Type",
        track_visibility="onchange",
        help="The amount that certain rates may increase.")
    termination_requested = fields.Date(
        string="Termination Requested Date",
        track_visibility="onchange",
        help="Date that a request for termination was received.")
    termination_date = fields.Date(
        string="Termination Date",
        track_visibility="onchange",
        help="Date that the contract was terminated.")
    reviewed_date = fields.Date(
        string="Reviewed Date", track_visibility="onchange")
    reviewed_user_id = fields.Many2one(
        "res.users", string="Reviewed By", track_visibility="onchange")
    approved_date = fields.Date(
        string="Approved Date", track_visibility="onchange")
    approved_user_id = fields.Many2one(
        "res.users", string="Approved By", track_visibility="onchange")
    currency_id = fields.Many2one("res.currency", string="Currency")
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=False,
        copy=True,
        help="The customer or vendor this agreement is related to.")
    partner_contact_id = fields.Many2one(
        "res.partner",
        string="Partner Contact",
        copy=True,
        help="The primary partner contact (If Applicable).")
    partner_contact_phone = fields.Char(
        related="partner_contact_id.phone", string="Partner Phone")
    partner_contact_email = fields.Char(
        related="partner_contact_id.email", string="Partner Email")
    company_contact_id = fields.Many2one(
        "res.partner",
        string="Company Contact",
        copy=True,
        help="The primary contact in the company.")
    company_contact_phone = fields.Char(
        related="company_contact_id.phone", string="Phone")
    company_contact_email = fields.Char(
        related="company_contact_id.email", string="Email")
    use_parties_content = fields.Boolean(
        string="Use parties content",
        help="Use custom content for parties")
    company_partner_id = fields.Many2one(
        related="company_id.partner_id", string="Company's Partner")

    def _get_default_parties(self):
        deftext = """
        <h3>Company Information</h3>
        <p>
        ${object.company_id.partner_id.name or ''}.<br>
        ${object.company_id.partner_id.street or ''} <br>
        ${object.company_id.partner_id.state_id.code or ''}
        ${object.company_id.partner_id.zip or ''}
        ${object.company_id.partner_id.city or ''}<br>
        ${object.company_id.partner_id.country_id.name or ''}.<br><br>
        Represented by <b>${object.company_contact_id.name or ''}.</b>
        </p>
        <p></p>
        <h3>Partner Information</h3>
        <p>
        ${object.partner_id.name or ''}.<br>
        ${object.partner_id.street or ''} <br>
        ${object.partner_id.state_id.code or ''}
        ${object.partner_id.zip or ''} ${object.partner_id.city or ''}<br>
        ${object.partner_id.country_id.name or ''}.<br><br>
        Represented by <b>${object.partner_contact_id.name or ''}.</b>
        </p>
        """
        return deftext

    parties = fields.Html(
        string="Parties",
        track_visibility="onchange",
        default=_get_default_parties,
        help="Parties of the agreement")
    dynamic_parties = fields.Html(
        compute="_compute_dynamic_parties",
        string="Dynamic Parties",
        help="Compute dynamic parties")
    agreement_type_id = fields.Many2one(
        track_visibility="onchange",
    )
    agreement_subtype_id = fields.Many2one(
        "agreement.subtype",
        string="Agreement Sub-type",
        track_visibility="onchange",
        help="Select the sub-type of this agreement. Sub-Types are related to "
        "agreement types.")
    product_ids = fields.Many2many(
        "product.template", string="Products & Services")
    assigned_user_id = fields.Many2one(
        "res.users",
        string="Assigned To",
        track_visibility="onchange",
        help="Select the user who manages this agreement.")
    company_signed_user_id = fields.Many2one(
        "res.users",
        string="Signed By",
        track_visibility="onchange",
        help="The user at our company who authorized/signed the agreement or "
        "contract.")
    partner_signed_user_id = fields.Many2one(
        "res.partner",
        string="Signed By (Partner)",
        track_visibility="onchange",
        help="Contact on the account that signed the agreement/contract.")
    parent_agreement_id = fields.Many2one(
        "agreement",
        string="Parent Agreement",
        help="Link this agreement to a parent agreement. For example if this "
        "agreement is an amendment to another agreement. This list will "
        "only show other agreements related to the same account.")
    renewal_type_id = fields.Many2one(
        "agreement.renewaltype",
        string="Renewal Type",
        track_visibility="onchange",
        help="Describes what happens after the contract expires.")
    recital_ids = fields.One2many(
        "agreement.recital", "agreement_id", string="Recitals", copy=True)
    sections_ids = fields.One2many(
        "agreement.section", "agreement_id", string="Sections", copy=True)
    clauses_ids = fields.One2many(
        "agreement.clause", "agreement_id", string="Clauses")
    appendix_ids = fields.One2many(
        "agreement.appendix", "agreement_id", string="Appendices", copy=True)
    previous_version_agreements_ids = fields.One2many(
        "agreement",
        "parent_agreement_id",
        string="Previous Versions",
        copy=False,
        domain=[("active", "=", False)])
    child_agreements_ids = fields.One2many(
        "agreement",
        "parent_agreement_id",
        string="Child Agreements",
        copy=False,
        domain=[("active", "=", True)])
    line_ids = fields.One2many(
        "agreement.line",
        "agreement_id",
        string="Products/Services",
        copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("inactive", "Inactive")],
        default="draft",
        track_visibility="always")
    notification_address_id = fields.Many2one(
        "res.partner",
        string="Notification Address",
        help="The address to send notificaitons to, if different from "
        "customer address.(Address Type = Other)")
    signed_contract_filename = fields.Char(string="Filename")
    signed_contract = fields.Binary(
        string="Signed Document", track_visibility="always")

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
    def _compute_dynamic_description(self):
        MailTemplates = self.env["mail.template"]
        for agreement in self:
            lang = agreement.partner_id.lang or "en_US"
            description = MailTemplates.with_context(
                lang=lang
            )._render_template(
                agreement.description, "agreement", agreement.id
            )
            agreement.dynamic_description = description

    @api.multi
    def _compute_dynamic_parties(self):
        MailTemplates = self.env["mail.template"]
        for agreement in self:
            lang = agreement.partner_id.lang or "en_US"
            parties = MailTemplates.with_context(
                lang=lang
            )._render_template(
                agreement.parties, "agreement", agreement.id
            )
            agreement.dynamic_parties = parties

    @api.multi
    def _compute_dynamic_special_terms(self):
        MailTemplates = self.env["mail.template"]
        for agreement in self:
            lang = agreement.partner_id.lang or "en_US"
            special_terms = MailTemplates.with_context(
                lang=lang
            )._render_template(
                agreement.special_terms, "agreement", agreement.id
            )
            agreement.dynamic_special_terms = special_terms

    # Used for Kanban grouped_by view
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env["agreement.stage"].search(
            [('stage_type', '=', 'agreement')])
        return stage_ids

    stage_id = fields.Many2one(
        "agreement.stage",
        string="Stage",
        group_expand="_read_group_stage_ids",
        help="Select the current stage of the agreement.",
        track_visibility="onchange",
        index=True)

    # Create New Version Button
    @api.multi
    def create_new_version(self, vals):
        for rec in self:
            if not rec.state == "draft":
                # Make sure status is draft
                rec.state = "draft"
            default_vals = {
                "name": "{} - OLD VERSION".format(rec.name),
                "active": False,
                "parent_agreement_id": rec.id,
            }
            # Make a current copy and mark it as old
            rec.copy(default=default_vals)
            # Increment the Version
            rec.version = rec.version + 1
        # Reset revision to 0 since it's a new version
        vals["revision"] = 0
        return super(Agreement, self).write(vals)

    def create_new_agreement(self):
        default_vals = {
            "name": "NEW",
            "active": True,
            "version": 1,
            "revision": 0,
            "state": "draft",
            "stage_id": self.env.ref("agreement_legal.agreement_stage_new").id,
        }
        res = self.copy(default=default_vals)
        res.sections_ids.mapped('clauses_ids').write({'agreement_id': res.id})
        return {
            "res_model": "agreement",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_id": res.id,
        }

    @api.model
    def create(self, vals):
        if vals.get("code", _("New")) == _("New"):
            vals["code"] = self.env["ir.sequence"].next_by_code(
                "agreement"
            ) or _("New")
        if not vals.get('stage_id'):
            vals["stage_id"] = \
                self.env.ref("agreement_legal.agreement_stage_new").id
        return super(Agreement, self).create(vals)

    # Increments the revision on each save action
    @api.multi
    def write(self, vals):
        vals["revision"] = self.revision + 1
        return super(Agreement, self).write(vals)
