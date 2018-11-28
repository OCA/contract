# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product1 = self.env.ref('product.product_product_1')
        self.product2 = self.env.ref('product.product_product_2')
        self.sale = self.env.ref('sale.sale_order_2')
        self.contract_template1 = self.env['account.analytic.contract'].create(
            {'name': 'Template 1'}
        )
        self.contract_template2 = self.env['account.analytic.contract'].create(
            {
                'name': 'Template 2',
                'recurring_invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'product_id': self.product2.id,
                            'name': 'Services from #START# to #END#',
                            'quantity': 1,
                            'uom_id': self.product2.uom_id.id,
                            'price_unit': 100,
                            'discount': 50,
                            'recurring_rule_type': 'yearly',
                            'recurring_interval': 1,
                        },
                    )
                ],
            }
        )
        self.product1.write(
            {
                'is_contract': True,
                'is_auto_renew': True,
                'contract_template_id': self.contract_template1.id,
            }
        )
        self.product2.write(
            {
                'is_contract': True,
                'contract_template_id': self.contract_template2.id,
            }
        )
        self.order_line1 = self.sale.order_line.filtered(
            lambda l: l.product_id == self.product1
        )
        self.order_line1.date_start = '2018-01-01'
        self.contract = self.env["account.analytic.account"].create(
            {
                "name": "Test Contract 2",
                "partner_id": self.sale.partner_id.id,
                "pricelist_id": self.sale.partner_id.property_product_pricelist.id,
                "recurring_invoices": True,
                "contract_type": "purchase",
                "contract_template_id": self.contract_template1.id,
                "recurring_invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": self.product1.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2016-02-15",
                            "recurring_next_date": "2016-02-29",
                        },
                    )
                ],
            }
        )
        self.contract_line = self.contract.recurring_invoice_line_ids[0]

    def test_compute_is_contract(self):
        """Sale Order should have is_contract true if one of its lines is
        contract"""
        self.assertTrue(self.sale.is_contract)

    def test_action_confirm_auto_renew_without_date_end(self):
        with self.assertRaises(ValidationError):
            self.sale.action_confirm()

    def test_action_confirm(self):
        """ It should create a contract for each contract template used in
        order_line """
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        contracts = self.sale.order_line.mapped('contract_id')
        self.assertEqual(len(contracts), 2)
        self.assertEqual(
            self.order_line1.contract_id.contract_template_id,
            self.contract_template1,
        )

    def test_sale_contract_count(self):
        """It should count contracts as many different contract template used
        in order_line"""
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(self.sale.contract_count, 2)

    def test_onchange_product(self):
        """ It should get recurrence invoicing info to the sale line from
        its product """
        self.order_line1.onchange_product()
        self.assertEqual(
            self.order_line1.recurring_rule_type,
            self.product1.recurring_rule_type,
        )
        self.assertEqual(
            self.order_line1.recurring_interval,
            self.product1.recurring_interval,
        )
        self.assertEqual(
            self.order_line1.recurring_invoicing_type,
            self.product1.recurring_invoicing_type,
        )
        self.assertEqual(self.order_line1.date_end, Date.to_date('2019-01-01'))

    def test_check_contract_sale_partner(self):
        """Can't link order line to a partner contract different then the
        order one"""
        contract2 = self.env['account.analytic.account'].create(
            {
                'name': 'Contract',
                'contract_template_id': self.contract_template2.id,
                'partner_id': self.sale.partner_id.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = contract2

    def test_check_contract_sale_contract_template(self):
        """Can't link order line to a contract with different contract
        template then the product one"""
        contract1 = self.env['account.analytic.account'].create(
            {
                'name': 'Contract',
                'contract_template_id': self.contract_template1.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = contract1

    def test_no_contract_proudct(self):
        """it should create contract for only product contract"""
        self.product1.is_contract = False
        self.sale.action_confirm()
        self.assertFalse(self.order_line1.contract_id)

    def test_sale_order_line_invoice_status(self):
        """Sale order line for contract product should have nothing to
        invoice as status"""
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(self.order_line1.invoice_status, 'no')

    def test_sale_order_invoice_status(self):
        """Sale order with only contract product should have nothing to
        invoice status directtly"""
        self.sale.order_line.filtered(
            lambda line: not line.product_id.is_contract
        ).unlink()
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(self.sale.invoice_status, 'no')

    def test_sale_order_create_invoice(self):
        """Should not invoice contract product on sale order create invoice"""
        self.product2.is_contract = False
        self.product2.invoice_policy = 'order'
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.sale.action_invoice_create()
        self.assertEqual(len(self.sale.invoice_ids), 1)
        invoice_line = self.sale.invoice_ids.invoice_line_ids.filtered(
            lambda line: line.product_id.is_contract
        )
        self.assertEqual(len(invoice_line), 0)

    def test_link_contract_invoice_to_sale_order(self):
        """It should link contract invoice to sale order"""
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        invoice = self.order_line1.contract_id.recurring_create_invoice()
        self.assertTrue(invoice in self.sale.invoice_ids)

    def test_contract_upsell(self):
        """Should stop contract line at sale order line start date"""
        self.order_line1.contract_id = self.contract
        self.order_line1.contract_line_id = self.contract_line
        self.contract_line.date_end = "2019-01-01"
        self.contract_line.is_auto_renew = "2019-01-01"
        self.order_line1.date_start = "2018-06-01"
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(
            self.contract_line.date_end, Date.to_date("2018-05-31")
        )
        self.assertFalse(self.contract_line.is_auto_renew)
        new_contract_line = self.env['account.analytic.invoice.line'].search(
            [('sale_order_line_id', '=', self.order_line1.id)]
        )
        self.assertEqual(
            self.contract_line.successor_contract_line_id, new_contract_line
        )
        self.assertEqual(
            new_contract_line.predecessor_contract_line_id, self.contract_line
        )
