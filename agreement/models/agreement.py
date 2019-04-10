# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class Agreement(models.Model):
    _name = 'agreement'
    _description = 'Agreement'

    code = fields.Char(required=True, copy=False)
    name = fields.Char(required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True,
        domain=[('parent_id', '=', False)])
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(default=True)
    signature_date = fields.Date()
    start_date = fields.Date()
    end_date = fields.Date()

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
