# Copyright 2019 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class CreateRevisionLineWizard(models.TransientModel):
    _name = 'create.revision.line.wizard'

    date_start = fields.Date(
        required=True,
    )
    date_end = fields.Date()
    variation_percent = fields.Float(
        digits=dp.get_precision('Product Price'),
        required=True,
        string='Variation %',
    )

    @api.multi
    def action_apply(self):
        contract_obj = self.env['account.analytic.account']
        line_obj = self.env['account.analytic.invoice.line']
        active_ids = self.env.context['active_ids']
        line_news = line_obj
        for item in contract_obj.browse(active_ids).mapped(
                'recurring_invoice_line_ids').filtered(
                lambda x: not x.automatic_price):
            line_news |= item.copy({
                'date_start': self.date_start,
                'date_end': self.date_end,
                'previous_revision_id': item.id,
                'price_unit': item.price_unit * (
                    1.0 + self.variation_percent / 100.0),
            })
            item.date_end = (fields.Date.from_string(self.date_start) -
                             relativedelta(days=1))
        action = self.env.ref(
            'contract.action_account_analytic_sale_overdue_all').read()[0]
        if len(active_ids) > 1:  # pragma: no cover
            action['domain'] = [('id', 'in', active_ids)]
        elif active_ids:
            action['views'] = [(
                self.env.ref('contract.account_analytic_account_sale_form').id,
                'form')]
            action['res_id'] = active_ids[0]
        return action
