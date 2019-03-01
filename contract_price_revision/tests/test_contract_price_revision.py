# Copyright 2019 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo.tests import common
from odoo import fields


class TestContractPriceRevision(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractPriceRevision, cls).setUpClass()
        partner = cls.env['res.partner'].create({
            'name': 'Partner test',
        })
        product = cls.env['product.product'].create({
            'name': 'Test Product',
        })
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Contract test',
            'partner_id': partner.id,
            'date_start': fields.Date.today(),
            'recurring_next_date': fields.Date.to_string(
                fields.date.today() + relativedelta(days=7)),
            'recurring_rule_type': 'monthly',
            'recurring_invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'quantity': 1.0,
                'uom_id': product.uom_id.id,
                'name': product.name,
                'price_unit': 33.0,
                'automatic_price': True,
            }), (0, 0, {
                'product_id': product.id,
                'quantity': 1.0,
                'uom_id': product.uom_id.id,
                'name': product.name,
                'price_unit': 25.0,
                'automatic_price': False,
            })]
        })

    def execute_wizard(self):
        wizard = self.env['create.revision.line.wizard'].create({
            'date_start': fields.Date.today(),
            'date_end': fields.Date.to_string(
                fields.date.today() + relativedelta(years=1)),
            'variation_percent': 100.0,
        })
        wizard.with_context(
            {'active_ids': [self.contract.id]}).action_apply()

    def test_contract_price_revision_wizard(self):
        self.assertEqual(len(self.contract.recurring_invoice_line_ids.ids), 2)
        self.execute_wizard()
        self.assertEqual(len(self.contract.recurring_invoice_line_ids.ids), 3)
        lines = self.contract.mapped('recurring_invoice_line_ids').filtered(
            lambda x: x.price_unit == 50.0)
        self.assertEqual(len(lines), 1)

    def test_contract_price_revision_invoicing(self):
        self.execute_wizard()
        self.contract.recurring_create_invoice()
        invoices = self.env['account.invoice'].search([
            ('contract_id', '=', self.contract.id)])
        self.assertEqual(len(invoices), 1)
        lines = invoices.mapped('invoice_line_ids')
        self.assertEqual(len(lines), 2)
        lines = lines.filtered(lambda x: x.price_unit == 50.0)
        self.assertEqual(len(lines), 1)
