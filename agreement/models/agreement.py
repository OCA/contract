# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, models, fields


class Agreement(models.Model):
    _name = 'agreement'
    _description = 'Agreement'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    code = fields.Char(required=True, track_visibility='onchange')
    name = fields.Char(required=True, track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict',
        domain=[('parent_id', '=', False)], track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    is_template = fields.Boolean(
        string="Is a Template?",
        default=False,
        copy=False,
        help="Set if the agreement is a template. "
        "Template agreements don't require a partner."
    )
    agreement_type_id = fields.Many2one(
        'agreement.type',
        string="Agreement Type",
        help="Select the type of agreement",
    )
    domain = fields.Selection(
        '_domain_selection', string='Domain', default='sale',
        track_visibility='onchange')
    active = fields.Boolean(default=True)
    signature_date = fields.Date(track_visibility='onchange')
    start_date = fields.Date(track_visibility='onchange')
    end_date = fields.Date(track_visibility='onchange')

    @api.model
    def _domain_selection(self):
        return [
            ('sale', _('Sale')),
            ('purchase', _('Purchase')),
            ]

    @api.onchange('agreement_type_id')
    def agreement_type_change(self):
        if self.agreement_type_id and self.agreement_type_id.domain:
            self.domain = self.agreement_type_id.domain

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.code:
                name = '[%s] %s' % (agr.code, agr.name)
            res.append((agr.id, name))
        return res

    _sql_constraints = [(
        'code_partner_company_unique',
        'unique(code, partner_id, company_id)',
        'This agreement code already exists for this partner!'
        )]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        """Always assign a value for code because is required"""
        default = dict(default or {})
        if default.get('code', False):
            return super().copy(default)
        default.setdefault('code', _("%s (copy)") % (self.code))
        return super().copy(default)
