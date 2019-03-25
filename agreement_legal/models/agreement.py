# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class Agreement(models.Model):
    _name = 'agreement'
    _inherit = ['mail.thread']

    def _default_stage_id(self):
        return self.env.ref('agreement.agreement_stage_new')

    # General
    name = fields.Char(
        string="Title",
        required=True
    )
    is_template = fields.Boolean(
        string="Is a Template?",
        default=False,
        copy=False,
        help="Make this agreement a template."
    )
    version = fields.Integer(
        string="Version",
        default=1,
        copy=False,
        help="The versions are used to keep track of document history and "
             "previous versions can be referenced."
    )
    revision = fields.Integer(
        string="Revision",
        default=0,
        copy=False,
        help="The revision will increase with every save event."
    )
    description = fields.Text(
        string="Description",
        track_visibility='onchange',
        help="Description of the agreement"
    )
    start_date = fields.Date(
        string="Start Date",
        track_visibility='onchange',
        help="When the agreement starts."
    )
    end_date = fields.Date(
        string="End Date",
        track_visibility='onchange',
        help="When the agreement ends."
    )
    color = fields.Integer()
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the agreement without "
             "removing it."
    )
    company_signed_date = fields.Date(
        string="Signed on",
        track_visibility='onchange',
        help="Date the contract was signed by Company."
    )
    partner_signed_date = fields.Date(
        string="Signed on",
        track_visibility='onchange',
        help="Date the contract was signed by the Partner."
    )
    term = fields.Integer(
        string="Term (Months)",
        track_visibility='onchange',
        help="Number of months this agreement/contract is in effect with the "
             "partner."
    )
    expiration_notice = fields.Integer(
        string="Exp. Notice (Days)",
        track_visibility='onchange',
        help="Number of Days before expiration to be notified."
    )
    change_notice = fields.Integer(
        string="Change Notice (Days)",
        track_visibility='onchange',
        help="Number of Days to be notified before changes."
    )
    special_terms = fields.Text(
        string="Special Terms",
        track_visibility='onchange',
        help="Any terms that you have agreed to and want to track on the "
             "agreement/contract."
    )
    contract_value = fields.Monetary(
        compute='_compute_contract_value',
        string="Contract Value",
        help="Total value of the contract over ther entire term.",
        store=True
    )
    reference = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: _('New'),
        track_visibility='onchange',
        help="ID used for internal contract tracking.")
    total_company_mrc = fields.Monetary(
        'Company MRC',
        currency_field='currency_id',
        help="Total company monthly recurring costs."
    )
    total_customer_mrc = fields.Monetary(
        'Customer MRC',
        currency_field='currency_id',
        help="Total custemer monthly recurring costs."
    )
    total_company_nrc = fields.Monetary(
        'Company NRC',
        currency_field='currency_id',
        help="Total company non-recurring costs."
    )
    total_customer_nrc = fields.Monetary(
        'Customer NRC',
        currency_field='currency_id',
        help="Total custemer non-monthly recurring costs."
    )
    increase_type_id = fields.Many2one(
        'agreement.increasetype',
        string="Increase Type",
        track_visibility='onchange',
        help="The amount that certain rates may increase."
    )
    termination_requested = fields.Date(
        string="Termination Requested Date",
        track_visibility='onchange',
        help="Date that a request for termination was received."
    )
    termination_date = fields.Date(
        string="Termination Date",
        track_visibility='onchange',
        help="Date that the contract was terminated."
    )
    reviewed_date = fields.Date(
        string="Reviewed Date",
        track_visibility='onchange'
    )
    reviewed_user_id = fields.Many2one(
        'res.users',
        string="Reviewed By",
        track_visibility='onchange'
    )
    approved_date = fields.Date(
        string="Approved Date",
        track_visibility='onchange'
    )
    approved_user_id = fields.Many2one(
        'res.users',
        string="Approved By",
        track_visibility='onchange'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Partmer",
        copy=True,
        help="The customer or vendor this agreement is related to."
    )
    company_partner_id = fields.Many2one(
        'res.partner',
        string="Company",
        copy=True,
        default=lambda self: self.env.user.company_id.partner_id
    )
    partner_contact_id = fields.Many2one(
        'res.partner',
        string="Partner Contact",
        copy=True,
        help="The primary partner contact (If Applicable)."
    )
    partner_contact_phone = fields.Char(
        related='partner_contact_id.phone',
        string="Phone"
    )
    partner_contact_email = fields.Char(
        related='partner_contact_id.email',
        string="Email"
    )
    company_contact_id = fields.Many2one(
        'res.partner',
        string="Company Contact",
        copy=True,
        help="The primary contact in the company."
    )
    company_contact_phone = fields.Char(
        related='company_contact_id.phone',
        string="Phone"
    )
    company_contact_email = fields.Char(
        related='company_contact_id.email',
        string="Email"
    )
    agreement_type_id = fields.Many2one(
        'agreement.type',
        string="Agreement Type",
        track_visibility='onchange',
        help="Select the type of agreement."
    )
    agreement_subtype_id = fields.Many2one(
        'agreement.subtype',
        string="Agreement Sub-type",
        track_visibility='onchange',
        help="Select the sub-type of this agreement. Sub-Types are related to "
             "agreement types."
    )
    product_ids = fields.Many2many(
        'product.template',
        string="Products & Services")
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sales Order",
        track_visibility='onchange',
        copy=False,
        help="Select the Sales Order that this agreement is related to."
    )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Payment Term",
        track_visibility='onchange',
        help="Terms of payments."
    )
    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned To",
        track_visibility='onchange',
        help="Select the user who manages this agreement."
    )
    company_signed_user_id = fields.Many2one(
        'res.users',
        string="Signed By",
        track_visibility='onchange',
        help="The user at our company who authorized/signed the agreement or "
             "contract."
    )
    partner_signed_user_id = fields.Many2one(
        'res.partner',
        string="Signed By",
        track_visibility='onchange',
        help="Contact on the account that signed the agreement/contract."
    )
    parent_agreement_id = fields.Many2one(
        'agreement',
        string="Parent Agreement",
        help="Link this agreement to a parent agreement. For example if this "
             "agreement is an amendment to another agreement. This list will "
             "only show other agreements related to the same account."
    )
    renewal_type_id = fields.Many2one(
        'agreement.renewaltype',
        string="Renewal Type",
        track_visibility='onchange',
        help="Describes what happens after the contract expires."
    )
    order_lines_services_ids = fields.One2many(
        related='sale_order_id.order_line',
        string="Service Order Lines",
        copy=False
    )
    sections_ids = fields.One2many(
        'agreement.section',
        'agreement_id',
        string="Sections",
        copy=True
    )
    clauses_ids = fields.One2many(
        'agreement.clause',
        'agreement_id',
        string="Clauses",
        copy=True
    )
    analytic_id = fields.Many2one('account.analytic.account',
                                  string='Analytic Account', index=True)
    analytic_line_ids = fields.One2many('account.analytic.line',
                                        'agreement_id',
                                        string='Revenues and Costs',
                                        copy=False)
    previous_version_agreements_ids = fields.One2many(
        'agreement',
        'parent_agreement_id',
        string="Child Agreements",
        copy=False,
        domain=[('active', '=', False)]
    )
    child_agreements_ids = fields.One2many(
        'agreement',
        'parent_agreement_id',
        string="Child Agreements",
        copy=False,
        domain=[('active', '=', True)]
    )
    products_ids = fields.Many2many(
        'product.template',
        string="Products",
        copy=False
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive')],
        default='draft',
        track_visibility='always'
    )
    notification_address_id = fields.Many2one(
        'res.partner',
        string="Notification Address",
        help="The address to send notificaitons to, if different from "
             "customer address.(Address Type = Other)"
    )
    signed_contract_filename = fields.Char(
        string="Filename"
    )
    signed_contract = fields.Binary(
        string="Signed Document",
        track_visibility='always'
    )

    # compute contract_value field
    @api.depends('total_customer_mrc', 'total_customer_nrc', 'term')
    def _compute_contract_value(self):
        for record in self:
            record.contract_value =\
                (record.total_customer_mrc * record.term) +\
                record.total_customer_nrc

    # compute total_company_mrc field
    @api.depends('order_lines_services_ids', 'sale_order_id')
    def _compute_company_mrc(self):
        order_lines = self.env['sale.order.line'].search(
            [('is_service', '=', True)])
        amount_total = sum(order_lines.mapped('purchase_price'))
        for record in self:
            record.total_company_mrc = amount_total

    # Used for Kanban grouped_by view
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['agreement.stage'].search([])
        return stage_ids

    stage_id = fields.Many2one(
        'agreement.stage',
        string="Stage",
        group_expand='_read_group_stage_ids',
        help="Select the current stage of the agreement.",
        track_visibility='onchange',
        index=True,
        default=lambda self: self._default_stage_id(),
    )

    # Create New Version Button
    @api.multi
    def create_new_version(self, vals):
        for rec in self:
            if not rec.state == 'draft':
                # Make sure status is draft
                rec.state = 'draft'
            default_vals = {'name': '{0} - OLD VERSION'.format(rec.name),
                            'active': False,
                            'parent_agreement_id': rec.id}
            # Make a current copy and mark it as old
            rec.copy(default=default_vals)
            # Increment the Version
            rec.version = rec.version + 1
        # Reset revision to 0 since it's a new version
        vals['revision'] = 0
        return super(Agreement, self).write(vals)

    def create_new_agreement(self):
        default_vals = {'name': 'NEW',
                        'active': True,
                        'version': 1,
                        'revision': 0,
                        'state': 'draft'}
        res = self.copy(default=default_vals)
        return {'res_model': 'agreement',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': res.id}

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = \
                self.env['ir.sequence'].next_by_code('agreement') or _('New')
        return super(Agreement, self).create(vals)

    # Increments the revision on each save action
    @api.multi
    def write(self, vals):
        vals['revision'] = self.revision + 1
        return super(Agreement, self).write(vals)
