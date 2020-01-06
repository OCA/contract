# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ContractAbstractContract(models.AbstractModel):
    _name = 'contract.abstract.contract'
    _description = 'Abstract Recurring Contract'

    # These fields will not be synced to the contract
    NO_SYNC = ['name', 'partner_id', 'company_id']

    @api.model
    def _get_default_invoice_incoterm(self):
        ''' Get the default incoterm for invoice. '''
        return self.env.company.incoterm_id

    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm',
        default=_get_default_invoice_incoterm,
        help='International Commercial Terms are a series of predefined commercial terms used in international transactions.')

    name = fields.Char(required=True)
    date = fields.Date( string='Signed Date', default=lambda self: fields.Date.today())

    # Needed for avoiding errors on several inherited behaviors
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", index=True
    )
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    currency_id = fields.Many2one(
        related="pricelist_id.currency_id",
        string="Pricelist currency",
        store=True,  )
    contract_type = fields.Selection(
        selection=[('sale', 'Customer'), ('purchase', 'Supplier')],
        default='sale',
        index=True,
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=lambda s: s._default_journal(),
        domain="[('type', '=', contract_type),"
        "('company_id', '=', company_id)]",
        index=True,
    )
    auto_post = fields.Boolean(string='Auto Post Invoice', default=False,
        help='If this checkbox is ticked, the generated invoice will have auto_post=True meaning that at the invoice date the invoice will be posted/validated')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            self._name
        ),
    )



    @api.onchange('contract_type')
    def _onchange_contract_type(self):
        if self.contract_type == 'purchase':
            self.contract_line_ids.filtered('automatic_price').update(
                {'automatic_price': False}
            )
        self.journal_id = self.env['account.journal'].search(
            [
                ('type', '=', self.contract_type),
                ('company_id', '=', self.company_id.id),
            ],
            limit=1,
        )

    @api.model
    def _default_journal(self):
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id
        )
        domain = [
            ('type', '=', self.contract_type),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)
