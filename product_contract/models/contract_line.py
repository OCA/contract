# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'
    _rec_name = 'display_name'

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        required=False,
        copy=False,
    )

    @api.multi
    def _prepare_invoice_line(self, invoice_id=False):
        res = super(AccountAnalyticInvoiceLine, self)._prepare_invoice_line(
            invoice_id=invoice_id
        )
        if self.sale_order_line_id and res:
            res['sale_line_ids'] = [(6, 0, [self.sale_order_line_id.id])]
        return res

    @api.multi
    def _get_auto_renew_rule_type(self):
        """monthly last day don't make sense for auto_renew_rule_type"""
        self.ensure_one()
        if self.recurring_rule_type == "monthlylastday":
            return "monthly"
        return self.recurring_rule_type

    @api.onchange('product_id')
    def _onchange_product_id_recurring_info(self):
        for rec in self:
            rec.date_start = fields.Date.today()
            if rec.product_id.is_contract:
                rec.recurring_rule_type = rec.product_id.recurring_rule_type
                rec.recurring_invoicing_type = (
                    rec.product_id.recurring_invoicing_type
                )
                rec.recurring_interval = 1
                rec.is_auto_renew = rec.product_id.is_auto_renew
                rec.auto_renew_interval = rec.product_id.default_qty
                rec.auto_renew_rule_type = rec._get_auto_renew_rule_type()
                rec.termination_notice_interval = (
                    rec.product_id.termination_notice_interval
                )
                rec.termination_notice_rule_type = (
                    rec.product_id.termination_notice_rule_type
                )

    @api.depends('name', 'date_start')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = ("%s - %s") % (rec.date_start, rec.name)
