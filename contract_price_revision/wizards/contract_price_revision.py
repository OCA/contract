# Copyright 2019 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class ContractPriceRevisionWizard(models.TransientModel):
    """ Update contract price based on percentage variation """
    _name = 'contract.price.revision.wizard'
    _description = "Wizard to update price based on percentage variation"

    date_start = fields.Date(
        required=True,
    )
    date_end = fields.Date()
    variation_percent = fields.Float(
        digits=dp.get_precision('Product Price'),
        required=True,
        string='Variation %',
    )

    def action_apply(self):
        ContractLine = self.env['contract.line']
        active_ids = self.env.context['active_ids']
        for line in self.env['contract.contract'].browse(active_ids).mapped(
                'contract_line_ids'):
            if (line.automatic_price or line.successor_contract_line_id or
                    not line.recurring_next_date):
                continue
            line.update({
                'date_end': self.date_start - relativedelta(days=1),
            })
            new_vals = line.copy_data({
                'date_start': self.date_start,
                'date_end': self.date_end,
                'predecessor_contract_line_id': line.id,
                'price_unit': line.price_unit * (
                    1.0 + self.variation_percent / 100.0),
            })[0]
            tmp_line = ContractLine.new(new_vals)
            tmp_line._onchange_date_start()
            new_line = ContractLine.create(
                tmp_line._convert_to_write(tmp_line._cache))
            line.update({
                'successor_contract_line_id': new_line.id,
            })
        action = self.env['ir.actions.act_window'].for_xml_id(
            'contract', 'action_customer_contract')
        action['domain'] = [('id', 'in', active_ids)]
        return action
