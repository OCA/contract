# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.doc._extensions.pyjsparser.parser import false


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one(
        'contract.contract',
        string='Recurring Contract',
        readonly=True
    )
    
    @api.depends('order_line.contract_id', 'state', 'contract_id')
    def _compute_need_contract_creation(self):
        for rec in self:
            if rec.state in ('sale', 'done'):
                if rec.contract_id:
                    rec.need_contract_creation = False
                else:
                    super(SaleOrder, rec)._compute_need_contract_creation()
              
              
    @api.multi
    def _prepare_contract_value(self, contract_template):
        res = super(SaleOrder, self)._prepare_contract_value(contract_template)
        res.update({'type': contract_template.type or 'invoice'})
        return res
    
    @api.multi
    def action_create_contract(self):
        sales = self.filtered(lambda so: len(so.contract_id) == 0)
        return super(SaleOrder, sales).action_create_contract()
    
    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        if self.contract_id:
            res.update({'journal_id': self.contract_id.journal_id.id})
        return res
    

